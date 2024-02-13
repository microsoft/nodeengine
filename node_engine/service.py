# Copyright (c) Microsoft. All rights reserved.

import asyncio
from typing import Any, AsyncGenerator

from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse

from node_engine.libs.runtime import Runtime
from node_engine.libs.utility import exit_flow_with_error
from node_engine.models.flow_definition import FlowDefinition
from node_engine.models.flow_step import FlowStep
from node_engine.models.sse_message import SSEMessage


def init(fastapi_app: FastAPI, local_files_root: str) -> None:
    """
    Adds node service engine endpoints to the FastAPI app.
    """
    app = fastapi_app
    runtime = Runtime(local_files_root)

    ####
    # Node Engine
    ####

    # Endpoint to invoke a flow
    @app.post("/invoke")
    async def invoke(
        flow_definition: FlowDefinition, request: Request
    ) -> FlowDefinition:
        tunnel_authorization = request.headers.get("X-Tunnel-Authorization")
        try:
            return await runtime.invoke(flow_definition, tunnel_authorization)
        except Exception as exception:
            flow_step = exit_flow_with_error(str(exception), flow_definition)
            return flow_step.flow_definition

    # Endpoint to invoke a component
    @app.post("/invoke_component")
    async def invoke_component(
        component_key: str, flow_definition: FlowDefinition, request: Request
    ) -> FlowStep:
        tunnel_authorization = request.headers.get("X-Tunnel-Authorization")
        try:
            return await runtime.invoke_component(
                flow_definition, component_key, tunnel_authorization
            )
        except Exception as exception:
            return exit_flow_with_error(str(exception), flow_definition)

    # Endpoint to list all available flow components
    @app.get("/registry")
    async def registry() -> list[dict[str, str]]:
        components = await runtime.registry.list_components()
        # only return key, label, description, and type
        return [
            dict(
                key=component.key,
                label=component.label,
                description=component.description,
                type=component.type,
            )
            for component in components
        ]

    ####
    # SSE
    ####

    # Endpoint to subscribe to SSE messages
    @app.get("/sse")
    async def sse(
        request: Request, session_id: str, connection_id: str | None = None
    ) -> EventSourceResponse:
        runtime.add_sse_connection(connection_id, session_id)

        async def event_stream() -> AsyncGenerator[dict[str, Any | str], Any]:
            while True:
                if await request.is_disconnected():
                    break

                if connection_id in runtime.sse_state.connections:
                    messages = runtime.sse_state.connections[connection_id]["messages"]
                    if len(messages) > 0:
                        message: SSEMessage = messages.pop(0)
                        yield {"event": message.event, "data": message.data}
                    else:
                        await asyncio.sleep(0.1)

        return EventSourceResponse(event_stream())

    # Endpoint to emit SSE messages from other services/components
    @app.post("/emit_sse_message")
    async def sse_message(message: SSEMessage) -> dict[str, str]:
        runtime.emit_sse_message(message.session_id, message)
        return {"status": "ok"}
