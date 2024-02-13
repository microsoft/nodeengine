# Copyright (c) Microsoft. All rights reserved.

import importlib.util

from node_engine.libs.component_loaders.component_loader import ComponentLoader
from node_engine.models.flow_definition import FlowDefinition
from node_engine.models.node_engine_component import NodeEngineComponent


class CodeComponentLoader:
    @staticmethod
    async def load(
        flow_definition: FlowDefinition,
        component_key: str,
        code: str,
        class_name: str,
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
            flow_definition, component_key, module, class_name, tunnel_authorization
        )
