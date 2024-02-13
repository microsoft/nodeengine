# Node Engine - Client

The 'client.py' file within the Node Engine defines the client-side interaction with the Node Engine service. It provides a Python class, NodeEngineClient, to interface with the service by initiating flow invocations, single component invocations, or emitting event messages.

## NodeEngineClient Class

- **Initialization**: Instantiate the client with a service_endpoint to specify the Node Engine service URL.

- **Invoke Flow**: The `invoke` method sends a FlowDefinition object to the Node Engine and initiates the execution of the defined flow.

- **Invoke Component**: The `invoke_component` method sends a FlowDefinition object and specifies a component to be invoked within the flow.

- **Emit Events**: The `emit` method allows the client to send event messages to the Node Engine, providing session_id, event type, and data.

Deprecated methods (the old approach) for direct invocations and emitting events are present but should be transitioned away from in favor of the NodeEngineClient class.

The file leverages httpx for HTTP client functionality and incorporates custom models from 'models.py' for FlowDefinition, FlowStatus, and FlowStep to structure interactions and handle responses from the Node Engine service.