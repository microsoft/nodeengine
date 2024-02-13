# Copyright (c) Microsoft. All rights reserved.

import importlib
import os
import pathlib
import traceback

import dotenv

from node_engine.libs.component_loaders.component_loader import ComponentLoader
from node_engine.models.flow_definition import FlowDefinition
from node_engine.models.node_engine_component import NodeEngineComponent

dotenv.load_dotenv()

# get path for parent of node_engine library
root_path = str(pathlib.Path(__file__).parent.parent.parent.parent.absolute())


class ModuleComponentLoader:
    @staticmethod
    async def load(
        flow_definition: FlowDefinition,
        component_key: str,
        module_name: str,
        class_name: str,
        local_files_root: str,
        tunnel_authorization: str | None = None,
    ) -> NodeEngineComponent:
        package = None

        # check if module exists in local files or any parent directories
        # until root directory is reached
        current_path = local_files_root
        while True:
            # check if module exists
            if os.path.isfile(
                os.path.join(current_path, "components", f"{module_name}.py")
            ):
                # get relative path
                relative_path = pathlib.Path(current_path).relative_to(
                    pathlib.Path(root_path)
                )
                # convert to dot notation
                package = ".".join(relative_path.parts + ("components",))
                break
            # check if at root
            if current_path == root_path:
                break
            # go up one level
            current_path = os.path.dirname(current_path)

        try:
            name = f".{module_name}"
            module = importlib.import_module(name, package)
        except Exception as exception:
            stacktrace = traceback.format_exc()
            raise Exception(
                f"Error importing module '{module_name}': {exception}. {stacktrace}"
            )

        return ComponentLoader.load(
            flow_definition, component_key, module, class_name, tunnel_authorization
        )

    @staticmethod
    def path_to_package(path: str) -> str:
        # get relative path
        relative_path = pathlib.Path(path).relative_to(pathlib.Path(root_path))
        # convert to dot notation
        package = ".".join(relative_path.parts + ("components",))
        return package
