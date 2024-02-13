# Copyright (c) Microsoft. All rights reserved.

from node_engine.models.node_engine_component import NodeEngineComponent
from node_engine.models.flow_step import FlowStep


class NextComponent(NodeEngineComponent):
    description = "Define the next component to run."

    reads_from = {
        "context": None,
        "config": {
            "next": {
                "type": "string",
                "description": "The key of the next component to run.",
                "required": True,
            },
            "limit": {
                "type": {
                    "max": {
                        "type": "integer",
                        "description": "The maximum number of times to allow this component to run.",
                        "required": True,
                    },
                    "key": {
                        "type": "string",
                        "description": "The key of the context variable to store the number of times this component has been run.",
                        "required": False,
                    },
                },
                "description": "The limit of times to run this component, to prevent infinite loops.",
                "required": False,
            },
        },
    }

    writes_to = None

    sample_input = {
        "key": "sample",
        "session_id": "123456",
        "flow": [
            {
                "key": "start",
                "name": "EmitEvents",
                "config": {
                    "events": [
                        {
                            "key": "event_1",
                            "name": "Event",
                            "config": {
                                "event": "event_1",
                            },
                        }
                    ],
                },
            },
            {
                "key": "next_component",
                "name": "NextComponent",
                "config": {
                    "next": "start",
                },
            },
        ],
    }

    async def execute(self) -> FlowStep:
        # set next component to run

        next = self.config.get("next")
        if not next:
            return self.exit_flow_with_error("Next component not defined")

        self.log(f"Next component set to '{next}'")

        limit = self.config.get("limit")
        if limit:
            limit_key = (
                limit["key"] if "key" in limit else f"{self.get_info()['name']}_limit"
            )

            limit_max = limit["max"]
            if limit_max is None:
                return self.exit_flow_with_error("Limit max not defined")

            limit_count = self.context.get(limit_key, 0) + 1

            if limit_count > limit_max:
                return self.exit_flow_with_error("Limit exceeded")

            self.context.set(limit_key, limit_count)

        return self.continue_flow(next)
