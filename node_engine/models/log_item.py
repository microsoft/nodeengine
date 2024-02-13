# Copyright (c) Microsoft. All rights reserved.

from enum import Enum

from pydantic import BaseModel


class LevelEnum(str, Enum):
    debug = "debug"
    info = "info"
    warning = "warning"
    error = "error"
    critical = "critical"


class LogItem(BaseModel):
    namespace: str
    level: LevelEnum
    message: str
    flow_definition: dict | None = None
