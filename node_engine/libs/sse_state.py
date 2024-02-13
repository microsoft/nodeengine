# Copyright (c) Microsoft. All rights reserved.

# State manager for server-sent events
# This is a simple implementation of a state manager for server-sent events.
# It is used by the SSE endpoints in the FastAPI server and the runtime in the Node Engine.


class SSEState:
    def __init__(self) -> None:
        # connections is a dictionary of connection_id: {session_id, messages}
        # messages is a list of messages to be sent to the client
        self.connections = {}

    # Add a connection to the state
    def add_connection(self, connection_id, session_id) -> None:
        if connection_id not in self.connections:
            self.connections[connection_id] = {
                "session_id": session_id,
                "messages": [],
            }
