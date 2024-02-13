# Copyright (c) Microsoft. All rights reserved.

from node_engine.models.flow_definition import FlowDefinition
from node_engine.models.node_engine_base_model import NodeEngineBaseModel


class FlowStep(NodeEngineBaseModel):
    next: str | None
    flow_definition: FlowDefinition
