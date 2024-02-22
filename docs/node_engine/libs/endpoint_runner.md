# Endpoint Runner Library

The `endpoint_runner.py` in the libs directory offers the `EndpointRunner` class, enabling execution of Node Engine components from remote endpoints. It is used to interface with external services or hosted components.

## EndpointRunner Class

- **Initialization**: Accepts a FlowDefinition, component configuration, the endpoint URL, component name and class, and an optional tunnel authorization parameter.

- **Execution**: Through the `execute` asynchronous method, the class manages the remote component execution workflow, handling the request and response processing.

- **Getting Component Source**: Additionally, the `_source_code` method retrieves the source code for the remotely hosted component, aiding in debugging and verification of remote execution.

- **Error Handling**: Implements robust error handling for cases where the remote invocation fails or returns an unexpected response.

This class is particularly useful for integrating remote components into flow definitions when using the Node Engine, thereby expanding its capabilities and interoperability with different parts of a distributed system.
