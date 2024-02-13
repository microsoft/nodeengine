# Copyright (c) Microsoft. All rights reserved.

import asyncio
import json
import logging

from node_engine.client import emit
from node_engine.libs.context import Context
from node_engine.models.flow_definition import FlowDefinition


class SSELoggerHandler(logging.Handler):
    def __init__(
        self, namespace: str, flow_definition: FlowDefinition, level=logging.DEBUG
    ) -> None:
        super().__init__()
        self.namespace = namespace
        self.flow_definition = flow_definition
        self.level = level

    def emit(self, record) -> None:
        context = Context(self.flow_definition)

        if not context.get("stream_log"):
            return

        data = {
            "namespace": self.namespace,
            "level": record.levelname.lower(),
            "message": record.msg,
        }

        if self.level == logging.DEBUG or record.levelno == logging.ERROR:
            data["flow_definition"] = self.flow_definition.model_dump()

        asyncio.ensure_future(
            emit(
                self.flow_definition.session_id,
                "log",
                json.dumps(data, indent=2),
            )
        )
