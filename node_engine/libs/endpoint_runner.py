# Copyright (c) Microsoft. All rights reserved.

from urllib.parse import urlencode, urljoin, urlparse

import httpx
from node_engine.client import RemoteExecutor

from node_engine.models.flow_definition import FlowDefinition
from node_engine.libs.node_engine_component import NodeEngineComponent
from node_engine.models.flow_step import FlowStep


class EndpointRunner(NodeEngineComponent):
    def __init__(
        self,
        flow_definition,
        config,
        endpoint,
        component_name,
        class_name,
        tunnel_authorization=None,
    ) -> None:
        super().__init__(flow_definition, config, executor=RemoteExecutor(endpoint))
        self.endpoint = endpoint
        self.component_name = component_name
        self.class_name = class_name
        self.tunnel_authorization = tunnel_authorization

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

    async def execute(self) -> FlowStep:
        # Run component from a remote endpoint.

        async with httpx.AsyncClient() as client:
            if self.tunnel_authorization:
                headers = {
                    "X-Tunnel-Authorization": f"tunnel {self.tunnel_authorization}"
                }
            else:
                headers = None

            uri = (
                urljoin(self.endpoint, "/invoke_component")
                + "?"
                + urlencode(
                    {
                        "component_name": self.component_name,
                        "class_name": self.class_name,
                        "component_key": self.component_key,
                    }
                )
            )

            self.validate_url(uri)
            response = await client.post(
                uri,
                json=self.flow_definition.model_dump(),
                headers=headers,
                timeout=None,
            )

        if response.status_code != 200:
            return self.exit_flow_with_error(
                f"Error in '{self.component_key}': {response.status_code} {response.reason_phrase} {response.text}"
            )

        data = response.json()
        updated_flow_definition = FlowDefinition(**data["flow_definition"])
        next = data["next"]

        return self.continue_flow(next, updated_flow_definition)

    async def _source_code(self) -> str:
        async with httpx.AsyncClient() as client:
            if self.tunnel_authorization:
                headers = {
                    "X-Tunnel-Authorization": f"tunnel {self.tunnel_authorization}"
                }
            else:
                headers = None

            uri = (
                urljoin(self.endpoint, "/get_component_source")
                + "?"
                + urlencode(
                    {
                        "component_name": self.component_name,
                        "class_name": self.class_name,
                        "component_key": self.component_key,
                        "with_line_numbers": True,
                    }
                )
            )

            self.validate_url(uri)
            response = await client.post(
                uri,
                json=self.flow_definition.model_dump(),
                headers=headers,
                timeout=None,
            )

        if response.status_code != 200:
            return ""

        return response.text
