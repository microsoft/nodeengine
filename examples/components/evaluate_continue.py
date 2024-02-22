# Copyright (c) Microsoft. All rights reserved.

import asyncio

from node_engine.libs.node_engine_component import NodeEngineComponent
from node_engine.models.flow_step import FlowStep


class EvaluateContinue(NodeEngineComponent):
    description = "Evaluate whether the flow should continue or not.  This is just a sample component to demonstrate the ability to perform flow control within a flow."

    reads_from = {
        "context": {
            "continued": {
                "type": "boolean",
                "description": "Whether the flow should continue or not.",
                "required": False,
            }
        },
    }

    writes_to = None

    sample_input = {
        "key": "sample",
        "session_id": "123456",
        "context": {
            "continued": True,
        },
        "flow": [
            {
                "key": "start",
                "name": "EvaluateContinue",
                "config": {
                    "outputs": {
                        "yes": "event_continue",
                        "no": "event_stop",
                    },
                },
            },
            {
                "key": "event_continue",
                "name": "EmitEvents",
                "config": {
                    "events": [
                        {
                            "event": "continue",
                        },
                    ],
                },
            },
            {
                "key": "event_stop",
                "name": "EmitEvents",
                "config": {
                    "events": [
                        {
                            "event": "stop",
                        },
                    ],
                },
            },
        ],
    }

    async def execute(self) -> FlowStep:
        # extract intent from message

        outputs = self.config.get("outputs")
        if not outputs:
            return self.exit_flow_with_error("outputs not found in component config")

        # Simulate some processing time
        await asyncio.sleep(1)

        continued = self.context.get("continued", False)
        next = outputs["yes"] if continued else outputs["no"]

        self.log("Evaluating continue: {}".format(continued))

        return self.continue_flow(next)
