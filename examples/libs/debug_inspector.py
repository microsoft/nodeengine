# Copyright (c) Microsoft. All rights reserved.

import inspect

from node_engine.libs.context import Context
from node_engine.libs.endpoint_runner import EndpointRunner
from node_engine.libs.registry import Registry
from node_engine.models.flow_component import FlowComponent
from node_engine.models.flow_definition import FlowDefinition
from node_engine.models.node_engine_component import NodeEngineComponent
from node_engine.models.log_item import LogItem


class DebugInspector:
    def __init__(
        self, local_files_root: str, flow_definition: FlowDefinition, error: str
    ) -> None:
        self.registry = Registry(local_files_root)
        self.error = error
        self.flow_definition = flow_definition
        self.flow = self.flow_definition.flow
        self.context = Context(flow_definition)
        self.status = self.flow_definition.status
        self.component_key: str | None = None

        # Get component info from status if it's there
        component_info = self.status.current_component
        if component_info is not None:
            self.component_name = component_info.name
            self.component_key = component_info.key
            self.component_config = component_info.config
        else:
            # Try to get component info from error.
            self.component_name = DebugInspector.get_component_name_from_error(error)
            if self.component_name is not None:
                self.component_key = DebugInspector.component_key_from_flow(
                    self.flow, self.component_name
                )

        self._component = None

    @classmethod
    def get_component_name_from_error(cls, error: str) -> str | None:
        if error.startswith("Error executing component: [") or error.startswith(
            "Error loading component: ["
        ):
            return error.split("[")[1].split("]")[0]

    @classmethod
    def component_key_from_flow(
        cls, flow: list[FlowComponent], component_name: str
    ) -> str | None:
        """Get component key from component name."""
        if component_name:
            for component in flow:
                if component.name == component_name:
                    return component.key

    def log(self, limit: int = 4, truncate_messages: int = -1) -> list[LogItem]:
        """
        Get log entries from flow status. Limit to last `limit` entries.
        Truncate messages to `truncate_messages` characters.
        """
        entries = self.status.log[-limit:]
        if truncate_messages > -1:
            for entry in entries:
                entry.message = entry.message[:truncate_messages] + "..."
        return entries

    async def component(self) -> NodeEngineComponent | None:
        if self._component is not None:
            return self._component

        if self.component_key is None:
            return None

        # Get component from registry.
        try:
            component = await self.registry.load_component(
                self.component_name or "unknown",
                self.flow_definition,
                self.component_key,
            )
            self._component = component
            return component
        except Exception:
            return None

    async def component_source(self) -> str | None:
        """Get component execute method code."""
        component = await self.component()

        # Get component's `execute` method source code.
        component_execute_source = None
        # TODO: Should we try to get component source from a file if we couldn't load the component?
        # check if component is of type EndpointRunner.
        # if so, get source from file.
        if component is not None:
            # check if instance of EndpointRunner
            if isinstance(component, EndpointRunner):
                code_string = await component.get_component_source()
            else:
                component_execute_source, start_line = inspect.getsourcelines(
                    component.execute
                )
                code_string = ""
                for i, line in enumerate(component_execute_source, start_line):
                    code_string += f"{i}: {line}"
            return code_string
