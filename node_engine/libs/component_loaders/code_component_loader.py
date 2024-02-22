# Copyright (c) Microsoft. All rights reserved.

import importlib.util

from node_engine.libs.component_loaders.component_loader import ComponentLoader
from node_engine.libs.node_engine_component import NodeEngineComponent
from node_engine.models.flow_definition import FlowDefinition
from node_engine.models.flow_executor import FlowExecutor


class CodeComponentLoader:
    @staticmethod
    def load(
        flow_definition: FlowDefinition,
        component_key: str,
        code: str,
        class_name: str,
        executor: FlowExecutor,
        tunnel_authorization: str | None = None,
    ) -> NodeEngineComponent:
        # convert code to module
        spec = importlib.util.spec_from_loader("helper", loader=None)
        if spec is None:
            raise Exception("Could not load spec from loader")
        module = importlib.util.module_from_spec(spec)
        if module is None:
            raise Exception("Could not load module from spec")
        exec(code, module.__dict__)

        return ComponentLoader.load(
            flow_definition,
            component_key,
            module,
            class_name,
            executor,
            tunnel_authorization,
        )
