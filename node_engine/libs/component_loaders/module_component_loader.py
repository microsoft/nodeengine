# Copyright (c) Microsoft. All rights reserved.

import importlib

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
        executor: FlowExecutor,
        tunnel_authorization: str | None = None,
    ) -> NodeEngineComponent:
        module = importlib.import_module(module_name)
        return ComponentLoader.load(
            flow_definition,
            component_key,
            module,
            class_name,
            executor,
            tunnel_authorization,
        )
