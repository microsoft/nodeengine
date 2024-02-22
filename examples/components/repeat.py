# Copyright (c) Microsoft. All rights reserved.

from node_engine.libs.node_engine_component import NodeEngineComponent
from node_engine.models.flow_step import FlowStep


class Repeat(NodeEngineComponent):
    description = ""

    default_config = {
        "include_debug": False,
    }

    reads_from = {
        "config": {
            "times": {
                "type": "int",
                "description": "How many times to run. Defaults to 1. Some other component will need to send back here.",
                "required": False,
            },
            "next": {
                "type": "string",
                "description": "The next step in the flow after repeats have been completed. Defaults to 'exit'.",
                "required": False,
            },
        },
    }

    writes_to = {
        "context": {
            "<repeat_component_key>_times": {
                "type": "int",
                "description": "This will be set/decremented each time this component is executed and removed from the context when completed.",
            }
        },
    }

    sample_input = {
        "key": "",
        "session_id": "test",
        "context": {
            "stream_log": "true",
        },
        "flow": [
            {
                "key": "repeat_1",
                "name": "Repeat",
                "config": {"times": 2, "next": "finish_up"},
            },
            {
                "key": "something",
                "name": "Something",
                "config": {
                    "next": "repeat_1",
                },
            },
            {
                "key": "finish_up",
                "name": "FinishUp",
            },
        ],
    }

    sample_output = {
        **sample_input,
        "context": {**sample_input["context"], "output": {}},
    }

    async def execute(self) -> FlowStep:
        iteration_key = f"{self.component_key}_times"

        total_times_str = self.config.get("times") or 1
        total_times = int(total_times_str)

        times = self.context.get(iteration_key, None)
        if times is None:
            times = total_times
            self.context.set(iteration_key, times)
        else:
            times = int(times) - 1

        if times >= 1:
            if self.config.get("include_debug", False):
                self.log.debug(f"Running {times} times.")
            self.context.set(iteration_key, times)
            return self.continue_flow()

        self.context.delete(iteration_key)
        return FlowStep(
            next=self.config.get("next", "exit"),
            flow_definition=self.flow_definition,
        )
