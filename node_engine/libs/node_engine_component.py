# Copyright (c) Microsoft. All rights reserved.

import inspect
import time
from abc import ABC, abstractmethod
from typing import Any

from node_engine.libs import debug_collector
from node_engine.libs.component_config import ComponentConfig
from node_engine.libs.context import Context
from node_engine.libs.log import Log
from node_engine.libs.telemetry import Telemetry
from node_engine.libs.utility import continue_flow, exit_flow_with_error
from node_engine.models.flow_definition import FlowDefinition
from node_engine.models.flow_event import FlowEvent
from node_engine.models.flow_executor import FlowExecutor
from node_engine.models.flow_step import FlowStep


class NodeEngineComponent(ABC):
    def __init__(
        self,
        flow_definition: FlowDefinition,
        component_key: str,
        executor: FlowExecutor,
        tunnel_authorization: str | None = None,
    ) -> None:
        self.flow_definition = flow_definition
        self.context = Context(self.flow_definition)
        self.status = self.flow_definition.status
        self.component_key = component_key
        self.tunnel_authorization = tunnel_authorization
        self.code = None
        self.runtime = executor
        self.log = Log(
            f"{self.__class__.__name__}:{component_key}",
            flow_definition=flow_definition,
            executor=executor,
        )

        default_config = getattr(self, "default_config", None)
        self.config = ComponentConfig(flow_definition, component_key, default_config)

        self.telemetry = Telemetry(
            flow_definition.session_id, flow_definition.key, component_key
        )

    @abstractmethod
    async def execute(self) -> FlowStep:
        pass

    async def invoke_execute(self, *args, **kwargs) -> FlowStep:
        """
        Run this method to execute the execute method. This allows for some
        common code to be executed before and after the method (tracing). We
        need to do this instead of using a meta-class so that we leave the
        actual execute method untouched for code-inspection.
        """
        # Code to execute before the method.
        start_time_ns = time.time_ns()

        # Call the original execute method.
        result = await self.execute(*args, **kwargs)

        # Code to execute after the method.
        end_time_ns = time.time_ns()

        # Populate trace information into the status.
        trace = {
            "elapsed_time_ms": (end_time_ns - start_time_ns) / 1_000_000,
            "component": {
                "key": self.component_key,
                "name": self.__class__.__name__,
            },
            "config": self.config.config,
            "context": self.flow_definition.context,
        }
        self.status.trace.append(trace)

        return result

    @classmethod
    def get_info(cls) -> dict[str, Any]:
        return {
            "name": cls.__name__,
            "description": getattr(cls, "description", None),
            "default_config": getattr(cls, "default_config", None),
            "reads_from": getattr(cls, "reads_from", None),
            "writes_to": getattr(cls, "writes_to", None),
            "sample_input": getattr(cls, "sample_input", None),
            "sample_output": getattr(cls, "sample_output", None),
        }

    @classmethod
    async def test(cls, executor: FlowExecutor) -> FlowStep | str:
        sample_input = cls.get_info().get("sample_input")
        if not sample_input:
            return "no sample input found"
        flow_definition = FlowDefinition(**sample_input)
        component_key = flow_definition.flow[0].key
        return await cls(flow_definition, component_key, executor=executor).execute()

    async def emit(self, event: str, data: str | None = None) -> None:
        await self.runtime.emit(
            event=FlowEvent(
                session_id=self.flow_definition.session_id, event=event, data=data or ""
            ),
        )

    async def invoke(self, flow_definition: FlowDefinition) -> FlowDefinition:
        return await self.runtime.invoke(flow_definition, self.tunnel_authorization)

    async def invoke_component(
        self, flow_definition: FlowDefinition, component_key: str
    ) -> FlowStep:
        return await self.runtime.invoke_component(
            flow_definition, component_key, self.tunnel_authorization
        )

    def exit_flow_with_error(self, message: str) -> FlowStep:
        debug_information = debug_collector.collect(
            message=message,
            flow_definition=self.flow_definition,
            component_source=self._source_code(),
            component_info=self.__class__.get_info(),
        )
        return exit_flow_with_error(
            message,
            self.flow_definition,
            log=self.log,
            debug_information=debug_information,
        )

    def continue_flow(
        self,
        next: str | None = None,
        updated_flow_definition: FlowDefinition | None = None,
    ) -> FlowStep:
        return continue_flow(next, updated_flow_definition or self.flow_definition)

    def _source_code(self) -> str:
        """
        Returns the source code of the execute method for debugging purposes.
        """
        component_execute_source, start_line = inspect.getsourcelines(self.execute)
        code_string = ""
        for i, line in enumerate(component_execute_source, start_line):
            code_string += f"{i}: {line}"
        return code_string
