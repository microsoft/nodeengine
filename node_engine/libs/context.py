# Copyright (c) Microsoft. All rights reserved.

import json
from typing import Any

from node_engine.models.flow_definition import FlowDefinition


class Context:
    def __init__(self, flow_definition: FlowDefinition, log=None) -> None:
        self.flow_definition = flow_definition
        self.log = log

    def get(self, key, default=None) -> Any:
        return self.flow_definition.context.get(key, default)

    def delete(self, key) -> None:
        if key in self.flow_definition.context:
            del self.flow_definition.context[key]

    def set(self, key, value) -> None:
        self.flow_definition.context[key] = value

    def has_key(self, key) -> bool:
        return key in self.flow_definition.context

    def validate_presence_of(self, key) -> bool:
        if not self.has_key(key):
            if self.log:
                self.log.error(f"{key} not present in context")
            return False
        return True

    def json(self) -> str:
        return json.dumps(self.flow_definition.context, indent=2)
