This is the main directory for the Node Engine core functionality. Here is a breakdown of its contents and their purpose:

## Files

- **service.py**: Contains the FastAPI service endpoints setup for the Node Engine. Defines endpoints for invoking flows, invoking components, listing components, and working with Server-Sent Events (SSE).
- **client.py**: A Python client library to interact with the Node Engine service, which provides asynchronous methods to invoke flows, invoke a single component, and emit SSE messages.
- **start.py**: The entry point for the Node Engine API server. Parses command-line arguments and sets up the FastAPI app with routes initialized from the service.

## Directories

- **libs**: A set of library modules that provide shared utilities and base classes for the Node Engine components.
- **models**: Data models that define the structure and typing for flow definitions, statuses, and other core constructs of the Node Engine.

## Expansion & Implementation
To write code to expand the Node Engine, developers can add new components by creating them in the `user` directory. The Node Engine utilizes a modular design, allowing for easy integration of additional components, and a client library is available to call the service. Flow definitions can be written dynamically, adapting to different needs. Any new features or experiments should be initially developed in the `/user` directory as custom components or libs and proven valuable before being incorporated into the core engine.

