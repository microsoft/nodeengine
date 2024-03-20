# Copyright (c) Microsoft. All rights reserved.

import json
import os

from node_engine.libs.component_loaders.code_component_loader import CodeComponentLoader
from node_engine.libs.component_loaders.endpoint_component_loader import (
    EndpointComponentLoader,
)
from node_engine.libs.component_loaders.module_component_loader import (
    ModuleComponentLoader,
)
from node_engine.libs.node_engine_component import NodeEngineComponent
from node_engine.models.component_registration import ComponentRegistration
from node_engine.models.flow_definition import FlowDefinition
from node_engine.models.flow_executor import FlowExecutor

registry_file_name = "registry.json"


class Registry:
    def __init__(self, root_path: str) -> None:
        # We assume the registry file will be found at <root_path>/registry.json.
        self.root_path = root_path

    # Load each time needed so that changes to the registry file are reflected
    def list_components(self) -> list[ComponentRegistration]:
        # helper: load components from local json file
        def load_from_file(registry_file) -> list[ComponentRegistration]:
            with open(registry_file, "rt") as file:
                component_definitions = [
                    ComponentRegistration(**component) for component in json.load(file)
                ]

            return component_definitions

        # Load components from registry file.
        registry_file_path = os.path.join(self.root_path, registry_file_name)
        if not os.path.isfile(registry_file_path):
            return []

        component_definitions = load_from_file(registry_file_path)

        # Sort components by key.
        sorted_component_definitions = sorted(
            component_definitions, key=lambda component: component.key
        )

        # Return sorted components.
        return sorted_component_definitions

    def load_component(
        self,
        key: str,
        flow_definition: FlowDefinition,
        component_key: str,
        executor: FlowExecutor,
        tunnel_authorization: str | None = None,
    ) -> NodeEngineComponent | None:
        # Get the component registration for the given key.
        component_registration = (
            next(
                (
                    component
                    for component in self.list_components()
                    if component.key == key
                ),
                None,
            )
            or None
        )

        if component_registration is None:
            return None

        # Load the component.
        match component_registration.type:
            case "endpoint":
                component = EndpointComponentLoader.load(
                    flow_definition,
                    component_key,
                    component_registration.config["endpoint"],
                    component_registration.config["component_name"],
                    component_registration.config["class_name"],
                    tunnel_authorization=tunnel_authorization,
                )
            case "module":
                component = ModuleComponentLoader.load(
                    flow_definition,
                    component_key,
                    component_registration.config["module"],
                    component_registration.config["class"],
                    executor=executor,
                    tunnel_authorization=tunnel_authorization,
                )
            case "code":
                component = CodeComponentLoader.load(
                    flow_definition,
                    component_key,
                    component_registration.config["code"],
                    component_registration.config["class"],
                    executor=executor,
                    tunnel_authorization=tunnel_authorization,
                )
            case _:
                raise Exception(
                    f"Component type '{component_registration.type}' not supported"
                )

        if not isinstance(component, NodeEngineComponent):
            raise Exception(
                f"Component is not a NodeEngineComponent: {component_registration.label}"
            )

        return component
