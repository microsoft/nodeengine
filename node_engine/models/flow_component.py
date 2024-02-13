# Copyright (c) Microsoft. All rights reserved.

from node_engine.models.node_engine_base_model import NodeEngineBaseModel


class FlowComponent(NodeEngineBaseModel):
    key: str
    name: str
    config: dict = {}
