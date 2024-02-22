# Node Engine - Service

## Endpoints:

1. **/invoke**:

   - Method: POST
   - Function: Invokes a flow based on a provided flow definition.
   - Inputs: `FlowDefinition` object and `Request`.
   - Outputs: Updated `FlowDefinition` with the results of the invoked flow.

2. **/invoke_component**:

   - Method: POST
   - Function: Invokes a single component within a flow.
   - Inputs: `component_key` (string), `FlowDefinition` object, and `Request`.
   - Outputs: A `FlowStep` object with the result of the invoked component.

3. **/registry**:

   - Method: GET
   - Function: Lists all components in the registry.
   - Outputs: List of dictionaries with key, label, description, and type of each component.

4. **/sse**:

   - Method: GET
   - Function: Subscribes to server-sent events based on `session_id` and optionally `connection_id`.
   - Inputs: `Request`, `session_id` (string), `connection_id` (string, optional).
   - Outputs: `EventSourceResponse` with SSE messages.

5. **/emit_sse_message**:
   - Method: POST
   - Function: Emits an SSE message for subscribed clients.
   - Inputs: `SSEMessage` object.
   - Outputs: Status of the message emission.

## Usage Examples:

To interact with these endpoints, one would require an instance of the Node Engine running with the FastAPI application to handle requests.

The 'service.py' file integrates the Node Engine within a FastAPI application, establishing endpoints for invoking flows, invoking components, querying the registry, subscribing to server-sent events (SSE), and emitting SSE messages.

## Endpoints

- **Invoke Flow**: POST `/invoke` endpoint to begin a flow execution with a FlowDefinition object.

- **Invoke Component**: POST `/invoke_component` endpoint to execute a specific component within a flow.

- **Flow Registry**: GET `/registry` endpoint providing a list of all registered flow components available within the engine.

- **Subscribe to SSE**: GET `/sse` for clients to subscribe to SSE messages based on session_id and connection_id.

- **Emit SSE Messages**: POST `/emit_sse_message` allows external services/components to send SSE messages.

## Implementation

- **Event Stream**: The event_stream generator handles SSE message delivery and client disconnections within the `/sse` subscription.

- **Runtime**: The `Runtime` class manages flow invocations, component executions, and event emissions.

- **Error Handling**: Exception handling is included to manage errors during flow or component invocation, ensuring the flow can exit cleanly with error details.

# Node Engine: service.py

This file is central to the operational capabilities of the Node Engine, and it should be structured and maintained to ensure robust, scalable, and flexible service interactions.
