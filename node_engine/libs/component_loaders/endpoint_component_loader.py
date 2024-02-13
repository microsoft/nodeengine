# Copyright (c) Microsoft. All rights reserved.

from node_engine.libs.endpoint_runner import EndpointRunner
from node_engine.models.flow_definition import FlowDefinition
from node_engine.models.node_engine_component import NodeEngineComponent


class EndpointComponentLoader:
    @staticmethod
    async def load(
        flow_definition: FlowDefinition,
        component_key: str,
        endpoint: str,
        component_name: str,
        class_name: str,
        tunnel_authorization: str | None = None,
    ) -> NodeEngineComponent:
        component = EndpointRunner(
            flow_definition,
            component_key,
            endpoint,
            component_name,
            class_name,
            tunnel_authorization,
        )

        return component
