# Copyright (c) Microsoft. All rights reserved.

from copy import deepcopy
from typing import Any

from node_engine.models.flow_definition import FlowDefinition
from node_engine.libs.utility import eval_templates_in_dict


class ComponentConfig:
    def __init__(
        self,
        flow_definition: FlowDefinition,
        component_key: str,
        defaults: dict | None = None,
    ) -> None:
        self.flow_definition = flow_definition
        for component in flow_definition.flow:
            if component.key == component_key:
                # Evaluate any templates in the config, replacing with values
                # from the context.
                self.config = deepcopy(component.config or {})
                self.config = eval_templates_in_dict(
                    self.config, self.flow_definition.context
                )
                break

        if self.config is None:
            raise Exception(f"Component with key {component_key} not found")

        self.defaults = defaults or {}

    def get(self, key, default=None) -> Any | None:
        # Get the value in the following order:
        if self.has_key(key):
            # 1. From the component config
            return self.config[key]
        else:
            return (
                # 2. From the default value passed into this call
                default
                if default is not None
                # 3. From the default value passed upon initialization
                else self.defaults[key]
                if key in self.defaults
                # 4. None
                else None
            )

    def has_key(self, key) -> bool:
        return key in self.config
