# Copyright (c) Microsoft. All rights reserved.

from urllib.parse import urlparse
import httpx

from node_engine.models.flow_definition import FlowDefinition
from node_engine.models.flow_status import FlowStatus
from node_engine.models.flow_step import FlowStep

# Replace this URL with your actual FastAPI server address.
default_endpoint = "http://localhost:8000"
invoke_path = "/invoke"
invoke_component_path = "/invoke_component"
emit_sse_message_path = "/emit_sse_message"


# This is the client that will be used by the user to interact with the Node Engine.
# New approach is to use the NodeEngineClient class to interact with the Node Engine.
# Old approach is to use the invoke, invoke_component, and emit functions, but this is deprecated.
class NodeEngineClient:
    def __init__(self, service_endpoint: str) -> None:
        self.service_endpoint = service_endpoint

    def validate_url(self, url):
        parsed_url = urlparse(url)

        # Check if the hostname or IP address is valid. Note: we trust "localhost" for simplicity
        # but the resolved IP should be validated for a more thorough check.
        host = parsed_url.hostname
        if host in ("localhost", "127.0.0.1") or host.startswith(("192.168.", "10.")):
            return

        # If not a local IP address, require HTTPS scheme
        if parsed_url.scheme.lower() != "https":
            raise ValueError(
                "Invalid URL scheme. HTTPS is required for non-local IP addresses."
            )

    async def invoke(
        self, flow_definition: FlowDefinition, tunnel_authorization: str | None = None
    ) -> FlowDefinition:
        self.validate_url(self.service_endpoint)
        async with httpx.AsyncClient() as client:
            if tunnel_authorization is not None:
                headers = {"X-Tunnel-Authorization": tunnel_authorization}
            else:
                headers = None

            invoke_url = f"{self.service_endpoint}{invoke_path}"

            response = await client.post(
                invoke_url,
                json=flow_definition.model_dump(),
                headers=headers,
                timeout=None,
            )

        try:
            return_flow_definition = FlowDefinition(**response.json())
        except Exception as e:
            error = f"{str(e)}. Response: {response}"
            return_flow_definition = FlowDefinition(
                key=flow_definition.key,
                session_id=flow_definition.session_id,
                flow=flow_definition.flow,
                context=flow_definition.context,
                status=FlowStatus(error=error),
            )
        return return_flow_definition

    async def invoke_component(
        self,
        flow_definition: FlowDefinition,
        component_key: str,
        tunnel_authorization: str | None = None,
    ) -> FlowStep:
        self.validate_url(self.service_endpoint)
        async with httpx.AsyncClient() as client:
            if tunnel_authorization:
                headers = {"X-Tunnel-Authorization": tunnel_authorization}
            else:
                headers = None

            invoke_component_url = f"{self.service_endpoint}{invoke_component_path}"

            response = await client.post(
                f"{invoke_component_url}?component_key={component_key}",
                json=flow_definition.model_dump(),
                headers=headers,
                timeout=None,
            )

        response_json = response.json()
        return FlowStep(
            flow_definition=FlowDefinition(**response_json["flow_definition"]),
            next=response_json["next"],
        )

    async def emit(self, session_id, event, data) -> httpx.Response:
        self.validate_url(self.service_endpoint)
        async with httpx.AsyncClient() as client:
            emit_sse_message_url = f"{self.service_endpoint}{emit_sse_message_path}"
            response = await client.post(
                emit_sse_message_url,
                json={"session_id": session_id, "event": event, "data": data},
                timeout=None,
            )

        return response


# Below is the old approach to interacting with the Node Engine.
# This is deprecated, please migrate to using the NodeEngineClient class instead.
# This version may be removed in the future.


async def invoke(
    flow_definition: FlowDefinition,
    tunnel_authorization: str | None = None,
) -> FlowDefinition:
    client = NodeEngineClient(default_endpoint)
    return await client.invoke(flow_definition, tunnel_authorization)


async def invoke_component(
    flow_definition: FlowDefinition,
    component_key: str,
    tunnel_authorization: str | None = None,
) -> FlowStep:
    client = NodeEngineClient(default_endpoint)
    return await client.invoke_component(
        flow_definition, component_key, tunnel_authorization
    )


async def emit(session_id, event, data) -> httpx.Response:
    client = NodeEngineClient(default_endpoint)
    return await client.emit(session_id, event, data)
