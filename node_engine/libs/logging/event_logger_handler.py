import asyncio
import json
import logging
from typing import Any

from node_engine.libs.context import Context
from node_engine.models.flow_definition import FlowDefinition
from node_engine.models.flow_event import FlowEvent
from node_engine.models.flow_executor import FlowExecutor


class EventLoggerHandler(logging.Handler):
    def __init__(
        self,
        namespace: str,
        flow_definition: FlowDefinition,
        executor: FlowExecutor,
        level=logging.DEBUG,
    ) -> None:
        super().__init__()
        self.namespace = namespace
        self.flow_definition = flow_definition
        self.level = level
        self.runtime = executor

        self.background_tasks: set[asyncio.Task] = set()

    def emit(self, record) -> None:
        context = Context(self.flow_definition)

        if not context.get("stream_log"):
            return

        data: dict[str, Any] = {
            "namespace": self.namespace,
            "level": record.levelname.lower(),
            "message": record.getMessage(),
        }

        if self.level == logging.DEBUG or record.levelno == logging.ERROR:
            data["flow_definition"] = self.flow_definition.model_dump(mode="json")

        message = FlowEvent(
            session_id=self.flow_definition.session_id,
            event="log",
            data=json.dumps(data),
        )

        task = asyncio.create_task(self.runtime.emit(message))
        # Add task to the set. This creates a strong reference.
        self.background_tasks.add(task)
        # To prevent keeping references to finished tasks forever,
        # make each task remove its own reference from the set after
        # completion:
        task.add_done_callback(self.background_tasks.discard)
