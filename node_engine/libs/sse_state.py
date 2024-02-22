# Copyright (c) Microsoft. All rights reserved.

import asyncio
from dataclasses import dataclass

from node_engine.models.flow_event import FlowEvent


@dataclass
class SSEConnection:
    session_id: str
    queue: asyncio.Queue[FlowEvent]


class SSEState:
    """
    State manager for server-sent events
    This is a simple implementation of a state manager for server-sent events.
    It is used by the SSE endpoints in the FastAPI server.
    """

    def __init__(self) -> None:
        self.connections: dict[str | None, SSEConnection] = {}

    def add_connection(self, connection_id, session_id) -> None:
        """
        Add a new connection
        """
        if connection_id in self.connections:
            return
        self.connections[connection_id] = SSEConnection(
            session_id=session_id, queue=asyncio.Queue()
        )
