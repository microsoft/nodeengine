# Node Engine - Start Script

The 'start.py' script facilitates the launching of the Node Engine service using Uvicorn with FastAPI.

## Features

- **Argument Parsing**: Parses command-line arguments, allowing the specification of a user alias that identifies the directory root for user-defined files and flows.

- **Service Initialization**: Invokes the `service.init` method to incorporate the Node Engine's endpoints into a FastAPI application instance.

- **Server Execution**: Utilizes `uvicorn.run` to initiate the FastAPI server, with the reload option enabled to aid developers by allowing dynamic updates without manual server restarts.

## Usage

Intended mainly for development and testing, this script configures the server environment for local accessibility of the Node Engine. It enables users to develop, test, and execute flow definitions in a user-specific or user-alias environment. To operationalize, run this script with the requisite command-line arguments to bootstrap the Node Engine server, which relies on the configured local or remote component registry.

This script is a critical part of the development and testing process, setting up a quick and convenient local server for flow experimentation and adjustments in the Node Engine ecosystem.