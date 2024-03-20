# Copyright (c) Microsoft. All rights reserved.

import importlib
import os
import pathlib
import traceback

from node_engine.libs.component_loaders.component_loader import ComponentLoader
from node_engine.libs.node_engine_component import NodeEngineComponent
from node_engine.models.flow_definition import FlowDefinition
from node_engine.models.flow_executor import FlowExecutor


class ModuleComponentLoader:
    @staticmethod
    def load(
        flow_definition: FlowDefinition,
        component_key: str,
        module_name: str,
        class_name: str,
        registry_root: str,
        executor: FlowExecutor,
        tunnel_authorization: str | None = None,
    ) -> NodeEngineComponent:
        try:
            module = importlib.import_module(module_name)

            return ComponentLoader.load(
                flow_definition,
                component_key,
                module,
                class_name,
                executor,
                tunnel_authorization,
            )
        except ModuleNotFoundError as e:
            if e.name != module_name:
                stacktrace = traceback.format_exc()
                raise Exception(
                    f"Error importing module '{module_name}': {e}. {stacktrace}"
                )

            pass

        # Check if module exists as a `components` dir off of registry_root.
        # This is the recommended way to set up Node Engine projects.
        if os.path.isfile(
            os.path.join(registry_root, "components", f"{module_name}.py")
        ):
            # Assumes the path that includes the `node_engine` dir is in the
            # system path which is how we recommend setting up Node Engine
            # projects.
            path_parts = pathlib.Path(registry_root).parts[-2:] + ("components",)
            # convert to dot notation
            package = ".".join(path_parts)

            try:
                name = f".{module_name}"
                module = importlib.import_module(name, package)
            except Exception as exception:
                stacktrace = traceback.format_exc()
                raise Exception(
                    f"Error importing module '{module_name}': {exception}. Trace: {stacktrace}"
                )

            return ComponentLoader.load(
                flow_definition,
                component_key,
                module,
                class_name,
                executor,
                tunnel_authorization,
            )

        stacktrace = traceback.format_exc()
        raise Exception(
            f"Module '{module_name}' not found in local file components dir: {stacktrace}"
        )
