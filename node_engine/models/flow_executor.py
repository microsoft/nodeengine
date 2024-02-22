from typing import Protocol

from node_engine.models.flow_definition import FlowDefinition
from node_engine.models.flow_event import FlowEvent
from node_engine.models.flow_step import FlowStep


class FlowExecutor(Protocol):
    async def invoke(
        self, flow_definition: FlowDefinition, tunnel_authorization: str | None = None
    ) -> FlowDefinition: ...

    async def invoke_component(
        self,
        flow_definition: FlowDefinition,
        component_key: str,
        tunnel_authorization: str | None = None,
    ) -> FlowStep: ...

    async def emit(self, event: FlowEvent, connection_id: str | None = None): ...
