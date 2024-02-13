# Node Engine

This document provides a comprehensive overview of the Node Engine system, its components, and the process of developing and expanding the Node Engine functionalities.

## Getting Started

Refer to the [Quickstart](../../README.md#quickstart) guide for initial setup instructions and how to run services and examples.

## Overview

- **Service**: The [Node Engine service](service.md) executes flow definitions as part of a larger system, enabling dynamic adaptation for varied caller requirements.
- **Registry**: The stand-in [registry](libs/registry.md) simulates a remote registry for component metadata and on-demand downloading. [registry.json](./node_engine/registry.json) can be edited to add components to the registry.
- **Client Library**: The [client library](client.md) simplifies service integration within Python codebases.
- **Examples**: The [notebooks directory](../../examples/notebooks/) contains examples for component development/testing with a smooth transition path from local to remote components and then to the Node Engine service.

## Development and Expansion

Node Engine is conceptualized for rapid experimentation and development. Core functionality should remain minimal, while custom components, libs, scripts, and flows are developed under app directories. Once validated for utility, these can be deployed as standalone services or merged into the engine if needed. Refer to the [Development guide](../../docs/DEVELOPMENT.md) for additional information.

The framework is designed with a focus on team experimentation and will incorporate insights for future enhancements.

## Core Concepts

- **Flow**: Triggered by a 'start' component, a flow comprises a sequence of components that process and modify a shared context object, concluding when 'exit' is reached.
- **Component**: Components are Python classes that execute the FlowDefinition and FlowComponent objects, making dynamic adjustments to flow execution permissible.
- **Design**: The Node Engine emphasizes simplicity and flexibility. Components are independent entities that should remain stateless whenever possible, allowing for both local and remote execution.
- **Background Processing**: The [`BackgroundProcess`](../../examples/components/background_process.py) component facilitates asynchronous task handling, allowing the main flow to continue unimpeded.
- **Events**: Components may communicate through SSE, utilizing the service's centralized event channel for updates to clients.
- **State Management**: State information should be stored contextually or in a persistent store rather than component configuration, ensuring the seamless propagation through a flow's lifecycle.

Each README file to be created for directories or files should maintain this level of detail and consistency in format and comprehensiveness to act as a complete guide for development and use of the Node Engine system.
