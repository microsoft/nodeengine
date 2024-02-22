# Copyright (c) Microsoft. All rights reserved.

from types import ModuleType

from node_engine.models.flow_definition import FlowDefinition
from node_engine.libs.node_engine_component import NodeEngineComponent
from node_engine.models.flow_executor import FlowExecutor


class ComponentLoader:
    @staticmethod
    def load(
        flow_definition: FlowDefinition,
        component_key: str,
        module: ModuleType,
        class_name: str,
        executor: FlowExecutor,
        tunnel_authorization: str | None = None,
    ) -> NodeEngineComponent:
        component_attribute = getattr(module, class_name)
        if component_attribute is None:
            raise Exception(f"Component '{class_name}' not found in module")

        try:
            component = component_attribute(
                flow_definition, component_key, executor, tunnel_authorization
            )
        except Exception as exception:
            raise Exception(
                f"Component '{class_name}' from module cannot to be initialized '{str(exception)}'"
            )

        return component
