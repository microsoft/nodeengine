# Copyright (c) Microsoft. All rights reserved.

from typing import Any

from pydantic import BaseModel

from node_engine.models.flow_component import FlowComponent
from node_engine.models.log_item import LogItem


class FlowStatus(BaseModel):
    current_component: FlowComponent | None = None
    error: str | None = None
    log: list[LogItem] = []
    trace: list[Any] = []
