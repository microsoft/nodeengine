# Copyright (c) Microsoft. All rights reserved.

import logging
from enum import IntEnum, unique
from typing import Any

from node_engine.libs.logging.sse_logger_handler import SSELoggerHandler
from node_engine.libs.logging.status_logger_handler import StatusLoggerHandler
from node_engine.models.flow_definition import FlowDefinition

DEBUG = logging.DEBUG  # 10
INFO = logging.INFO  # 20
WARNING = logging.WARNING  # 30
ERROR = logging.ERROR  # 40
CRITICAL = logging.CRITICAL  # 50


@unique
class LogLevel(IntEnum):
    DEBUG = DEBUG
    INFO = INFO
    WARNING = WARNING
    ERROR = ERROR
    CRITICAL = CRITICAL

    @classmethod
    def from_string(cls, str) -> "LogLevel":
        return cls[str.upper()]

    @classmethod
    def active(cls, set_level, level) -> Any:
        return set_level <= level


class Log(logging.Logger):
    def __init__(
        self, namespace: str, flow_definition: FlowDefinition, level=LogLevel.DEBUG
    ):
        super().__init__(namespace, level.value)
        self.addHandler(StatusLoggerHandler(namespace, flow_definition))
        self.addHandler(SSELoggerHandler(namespace, flow_definition))

    def __call__(self, message, *args, **kwargs) -> None:
        self.info(message, *args, **kwargs)

    def active(self, level) -> Any:
        return LogLevel.active(self.level, level)


# We pass around the string representation of the log level, but
def get_log_level(str) -> int:
    return LogLevel[str.upper()].value
