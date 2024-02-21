# Development

In addition to the steps outlined in the [quickstart](../README.md#quickstart), the following is provided to help with development and testing of new components, definitions, and scripts.

Package dependencies are specified in the `pyproject.toml` file. Add new dependencies here.

## App Directories

App Directories are a way to organize a set of components and definitions into a single directory that contains any custom files needed for the experience you are working on. This includes custom `registry.json`, components, definitions, libs, and scripts.

When loading the service from a script in an app directory, you can pass in a `registry_root` parameter to specify the root directory for the app. This will be the starting location for searching for any custom `registry.json` or component files. If not specified, the service will look for a registry in the current folder.

Example:

    # Enter Node Engine root directory
    cd <root of repo>

    # Activate python virtual environment
    source .venv/bin/activate

    # Create App Directory "myapp1"
    mkdir myapp1

    # Create empty registry for the new app
    touch myapp1/registry.json

    # Start service using "myapp1" component registry
    node_engine_service --registry_root myapp1

When looking for `registry.json`, Node Engine service starts by looking in `registry_root` directory, searching up the directory tree until it finds a `registry.json` file. Each `registry.json` found is merged with the previous one, with the first one found taking precedence. This allows you to have a base `registry.json` file and then override it with a custom `registry.json` file in an app directory. The default `registry.json` file in the node_engine directory is merged last.

When a component is loaded, it will start by looking for a `components` directory in the `registry_root` directory. If it exists, it will check to see if the desired component file also exists within that directory. If so, it will use that version. If not, it will continue this pattern and search up the directory tree until it finds a matching component file. If no component file is found, it will then search the default `./node_engine/components` directory.

## Service API

OpenAPI docs are available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) when the service is running.

## Creating components

Ultimately, the goal is to be able to **develop and test components** locally and then deploy them to a remote service for use in production. The following workflows are ones that we've found to be helpful in developing and testing new components.

### Notebook workflow: develop/test a component inside a Jupyter notebook

- Copy one of the [example notebooks](../examples/notebooks/) to a new notebook.
- Run the first code cell to set up the environment and to enable support for exporting your component.
- Modify the main code cell to create your new component, making sure to set the component class name.
- Run the main code cell to create your component in the notebook and to export a copy for use locally.
- Modify the test cell to provide a sample config and context and then run the cell to test your component within the notebook.
- Iterate as needed.
- Once satisfied that the component is working as expected with test config/context, add the component to the registry.json file.
- Update a flow config to use your new component and test it in the Node Engine service.
- Iterate as needed.
- If your component is to be added as a built-in component for the Node Engine service, copy it to the [node_engine/components](../node_engine/components) directory and update the registry.json to point to the new location/type.

### Code-only workflow

The notebook workflow above is not required (though may be helpful and good practice) and you can instead create your component directly in a Python file.

## Debugging

### Debug local script files via debugpy

This is good for debugging test scripts (non-service code)

- Insert `-m debugpy --listen 5678 --wait-for-client` between `python3` and the script to call. For example if your script is `examples/scripts/test-simple-chat.py "my-session-1" "ok, thanks!"`

      python3 -m debugpy --listen 5678 --wait-for-client examples/scripts/test-simple-chat.py "my-session-1" "ok, thanks!"

- Attach to the process via VS Code (Shift+Ctrl+D and choose 'Attach').

### Semantic Debug agent

We created an agent to help you debug your flows and components. You can run it
in a terminal with:

    python3 examples/scripts/debug-service.py <session_id>

The debug agent will connect to the Node Engine Service and listen to any logs
emitted via SSE for the given session. It will attempt to debug any error
message received.

## Optional services

### Dev Tunnels for remote service and flow with local components

[Azure dev tunnels](https://learn.microsoft.com/azure/developer/dev-tunnels) allow you to expose your local services to the Internet for testing with remote services and components. See the [dev tunnels quickstart](https://learn.microsoft.com/azure/developer/dev-tunnels/get-started) for instructions on installing. Ensure that you can run `devtunnel` on your command prompt before completing the next steps. You may find it easiest to download the [devtunnel binary](https://aka.ms/TunnelsCliDownload/win-x64) and add it to your path.

- `devtunnel user login` // login to your Microsoft AAD account
- `devtunnel create --port 8000 --protocol http --description="Node Engine"` // create a tunnel for the service running locally
- `devtunnel access create --tenant` // enable AAD authentication for the tunnel
- `devtunnel host` // start the tunnel

Note the url for the tunnel. You can update your component registry entries with this value to allow the Node Engine to load components from your local machine.

To authenticate with the tunnel, you will need an access token. You can generate one with the following commands:

- `devtunnel token tunnel --scope connect` // generate token for the tunnel

Tokens are valid for 24 hours and will need to be regenerated after that time. Pass the access token to any calls to the Node Engine service to authenticate with the tunnel. Use the `X-Tunnel-Authorization` header to pass the token.

Format:
`X-Tunnel-Authorization: tunnel <token>`
