# Runtime Library

The `runtime.py` file is central to the Node Engine's operation, encapsulating the execution logic and runtime management of flows and components.

## Runtime Class

- **Initialization**: Instantiates a runtime with a reference to the local files' root directory.

- **Flow Invocation**: The `invoke` method starts and manages the entire execution of a flow, orchestrating component execution and handling the flow context.

- **Add SSE Connection**: `add_sse_connection` method for registering SSE connections to manage real-time updates.

- **Emit SSE Messages**: The `emit_sse_message` function is responsible for sending messages to clients through the server-sent events channel.

- **Invoke Component**: Facilitates invoking a specific component within a flow through the `invoke_component` method.

- **Private Methods**: Includes a `__execute_next` method providing sequential execution logic of the components in a flow definition.

The Runtime class represents the core operational functionality of the Node Engine. It provides the mechanisms to execute and manage flows and their components in both synchronous and asynchronous fashions.