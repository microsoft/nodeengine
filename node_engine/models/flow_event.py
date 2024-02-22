# Copyright (c) Microsoft. All rights reserved.

from node_engine.models.node_engine_base_model import NodeEngineBaseModel


class FlowEvent(NodeEngineBaseModel):
    session_id: str
    event: str
    data: str
