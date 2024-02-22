# Copyright (c) Microsoft. All rights reserved.

import logging
from typing import Optional

from node_engine.models.flow_definition import FlowDefinition
from node_engine.models.log_item import LevelEnum, LogItem


class StatusLoggerHandler(logging.Handler):
    def __init__(
        self, namespace: str, flow_definition: Optional[FlowDefinition]
    ) -> None:
        super().__init__()
        self.namespace = namespace
        self.log = flow_definition.status.log if flow_definition else None

    def emit(self, record) -> None:
        if not self.log:
            return

        self.log.append(
            LogItem(
                namespace=self.namespace,
                level=LevelEnum[record.levelname.upper()],
                message=record.getMessage(),
            )
        )
