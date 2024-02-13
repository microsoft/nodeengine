# Registry Library

In the libs directory, `registry.py` provides the classes necessary for managing component registrations within the Node Engine. It interacts with a local or remote registry file to register and load flow components dynamically.

## Registry Class

- **Initialization**: Constructs the Registry with a specified root directory for local files.

- **Component Listing**: The `list_components` method assembles a list of all components available by aggregating registrations from a local JSON file and merging with any additional components.

- **Component Loading**: The `load_component` method is responsible for constructing instances of flow components based on their registration information and given parameters from the flow's definition.

- **Supported Types**: The registry supports different types of components such as endpoints, modules, and code, utilizing respective loader classes like `EndpointComponentLoader`, `ModuleComponentLoader`, and `CodeComponentLoader`.

This registry mechanism is crucial for the modularity and extensibility of the Node Engine, providing a dynamic way to integrate new components and handle their configurations.