# Copyright (c) Microsoft. All rights reserved.

import logging
import logging.handlers
from enum import IntEnum, unique
from typing import Any

from node_engine.libs.logging.flow_log_handler import FlowLogHandler
from node_engine.models.flow_definition import FlowDefinition
from node_engine.models.flow_executor import FlowExecutor

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


flow_logger = logging.getLogger("node_engine.flow")


class FlowLoggerAdapter(logging.LoggerAdapter):
    """Logger adapter that adds flow information to log messages."""

    def __init__(
        self,
        logger: Any,
        flow_definition: FlowDefinition,
        executor: FlowExecutor,
        component_label: str,
    ) -> None:
        super().__init__(logger)
        self._flow_definition = flow_definition
        self._executor = executor
        self._component_label = component_label

    def process(self, msg, kwargs):
        if self._component_label:
            return (
                "s:%s | f:%s | c:%s | %s"
                % (
                    self._flow_definition.session_id,
                    self._flow_definition.key,
                    self._component_label,
                    msg,
                ),
                kwargs,
            )

        return (
            "s:%s | f:%s | %s"
            % (self._flow_definition.session_id, self._flow_definition.key, msg),
            kwargs,
        )

    def __call__(self, message, *args, **kwargs) -> None:
        self.info(message, *args, **kwargs)


class FlowLogger(logging.Logger):
    """Logger that forwards log records to FlowLogHandler."""

    def __init__(
        self,
        name: str,
        flow_definition: FlowDefinition,
        executor: FlowExecutor,
        parent: logging.Logger,
        level=LogLevel.DEBUG,
    ):
        super().__init__(name, level.value)
        self.parent = parent
        self.addHandler(FlowLogHandler(flow_definition, executor))


def get_flow_logger(
    namespace: str,
    flow_definition: FlowDefinition,
    executor: FlowExecutor,
) -> FlowLoggerAdapter:
    namespace = ".".join(["node_engine", "flow", namespace])
    logger = FlowLogger(namespace, flow_definition, executor, flow_logger)
    return FlowLoggerAdapter(
        logger,
        flow_definition=flow_definition,
        executor=executor,
        component_label="",
    )


def get_component_logger(
    component_class: type,
    component_key: str,
    flow_definition: FlowDefinition,
    executor: FlowExecutor,
) -> FlowLoggerAdapter:
    namespace = "node_engine.flow.component"
    logger = FlowLogger(namespace, flow_definition, executor, flow_logger)
    return FlowLoggerAdapter(
        logger,
        flow_definition=flow_definition,
        executor=executor,
        component_label=f"{component_class.__name__}:{component_key}",
    )
