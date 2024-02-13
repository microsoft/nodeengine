# Copyright (c) Microsoft. All rights reserved.

import uuid

from pydantic import Field

from node_engine.models.component_registration import ComponentRegistration
from node_engine.models.flow_component import FlowComponent
from node_engine.models.node_engine_base_model import NodeEngineBaseModel
from node_engine.models.flow_status import FlowStatus


class FlowDefinition(NodeEngineBaseModel):
    key: str
    session_id: str = str(uuid.uuid4())
    flow: list[FlowComponent]
    registry: list[ComponentRegistration] | None = None
    context: dict = {}
    status: FlowStatus = Field(default=FlowStatus())
