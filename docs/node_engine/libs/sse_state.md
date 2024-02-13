# SSE State Library

`sse_state.py` in the libs directory manages the state for server-sent events (SSE) within the Node Engine. It is crucial for the real-time interaction between the server and connected clients during flow execution.

## SSEState Class

- **Initialization**: Instantiates an object that holds connections, which include session IDs and associated messages to be sent to clients.

- **Connection Management**: Offers a method `add_connection` for adding new connections to the state, ensuring the ability to track and send messages appropriately.

This state management for SSE is essential for the Node Engine when providing real-time updates and interactions, which are integral for certain components that require ongoing communication with client-side applications.