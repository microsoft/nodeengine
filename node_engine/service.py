# Copyright (c) Microsoft. All rights reserved.

import asyncio
from typing import Any, AsyncGenerator

from fastapi import FastAPI, Request
from sse_starlette.sse import EventSourceResponse

from node_engine.libs.runtime import Runtime
from node_engine.libs.sse_state import SSEState
from node_engine.libs.utility import exit_flow_with_error
from node_engine.models.flow_definition import FlowDefinition
from node_engine.models.flow_event import FlowEvent
from node_engine.models.flow_step import FlowStep


def init(fastapi_app: FastAPI, registry_root: str) -> None:
    """
    Adds node engine service endpoints to the FastAPI app.
    """
    app = fastapi_app
    runtime = Runtime(registry_root)
    sse_state = SSEState()

    @app.post("/invoke", description="Invoke a flow")
    async def invoke(
        flow_definition: FlowDefinition, request: Request
    ) -> FlowDefinition:
        tunnel_authorization = request.headers.get("X-Tunnel-Authorization")
        try:
            return await runtime.invoke(flow_definition, tunnel_authorization)
        except Exception as exception:
            flow_step = exit_flow_with_error(str(exception), flow_definition)
            return flow_step.flow_definition

    @app.post("/invoke_component", description="Invoke a component")
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

    @app.get("/registry", description="List all available flow components")
    async def registry() -> list[dict[str, str]]:
        components = runtime.registry.list_components()
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

    @app.get(
        "/sse", description="Subscribe to flow events using Server-Sent Events (SSE)"
    )
    async def sse(
        request: Request, session_id: str, connection_id: str | None = None
    ) -> EventSourceResponse:
        sse_state.add_connection(connection_id, session_id)
        runtime.add_event_consumer(
            session_id, sse_state.connections[connection_id].queue, connection_id
        )

        async def event_stream() -> AsyncGenerator[dict[str, Any | str], Any]:
            while True:
                if await request.is_disconnected():
                    break

                connection = sse_state.connections.get(connection_id)
                if not connection:
                    await asyncio.sleep(0.1)
                    continue

                try:
                    async with asyncio.timeout(1):
                        message = await connection.queue.get()
                except asyncio.TimeoutError:
                    continue

                connection.queue.task_done()
                yield {"event": message.event, "data": message.data}

        return EventSourceResponse(event_stream())

    @app.post(
        "/emit_sse_message",
        description="Emit a flow event from other services/components",
    )
    async def sse_message(
        event: FlowEvent, connection_id: str | None = None
    ) -> dict[str, str]:
        await runtime.emit(event, connection_id=connection_id)
        return {"status": "ok"}
