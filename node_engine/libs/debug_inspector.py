# Copyright (c) Microsoft. All rights reserved.

from node_engine.libs.context import Context
from node_engine.models.flow_component import FlowComponent
from node_engine.models.flow_definition import FlowDefinition
from node_engine.models.log_item import LogItem


class DebugInspector:
    def __init__(
        self,
        flow_definition: FlowDefinition,
        error: str,
    ) -> None:
        self.error = error
        self.flow_definition = flow_definition
        self.flow = self.flow_definition.flow
        self.context = Context(flow_definition)
        self.status = self.flow_definition.status
        self.component_key: str | None = None

        # Get component info from status if it's there
        component_info = self.status.current_component
        if component_info is not None:
            self.component_name = component_info.name
            self.component_key = component_info.key
            self.component_config = component_info.config
        else:
            # Try to get component info from error.
            self.component_name = DebugInspector.get_component_name_from_error(error)
            if self.component_name is not None:
                self.component_key = DebugInspector.component_key_from_flow(
                    self.flow, self.component_name
                )

    @classmethod
    def get_component_name_from_error(cls, error: str) -> str | None:
        if error.startswith("Error executing component: [") or error.startswith(
            "Error loading component: ["
        ):
            return error.split("[")[1].split("]")[0]

    @classmethod
    def component_key_from_flow(
        cls, flow: list[FlowComponent], component_name: str
    ) -> str | None:
        """Get component key from component name."""
        if component_name:
            for component in flow:
                if component.name == component_name:
                    return component.key

    def log(self, limit: int = 4, truncate_messages: int = -1) -> list[LogItem]:
        """
        Get log entries from flow status. Limit to last `limit` entries.
        Truncate messages to `truncate_messages` characters.
        """
        entries = self.status.log[-limit:]
        if truncate_messages > -1:
            for entry in entries:
                entry.message = entry.message[:truncate_messages] + "..."
        return entries
