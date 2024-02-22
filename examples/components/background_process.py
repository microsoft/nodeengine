# Copyright (c) Microsoft. All rights reserved.

import asyncio

from node_engine.models.flow_definition import FlowDefinition
from node_engine.libs.node_engine_component import NodeEngineComponent
from node_engine.models.flow_step import FlowStep


class BackgroundProcess(NodeEngineComponent):
    description = "Run a flow in the background."

    reads_from = {
        "context": None,
        "config": {
            "flow": {
                "type": "list",
                "description": "The flow to run in the background.",
                "required": True,
            }
        },
    }

    writes_to = None

    sample_input = {
        "key": "sample",
        "session_id": "123456",
        "context": {
            "messages": [
                {
                    "sender": "user",
                    "content": "Hello, can you help me with something?",
                },
                {
                    "sender": "agent",
                    "content": "Sure, what can I help you with?",
                },
            ],
        },
        "flow": [
            {
                "key": "start",
                "name": "BackgroundProcess",
                "config": {
                    "flow": [
                        {"key": "start", "name": "ProcessMemories"},
                    ],
                },
            },
        ],
    }

    async def execute(self) -> FlowStep:
        # run background process

        self.log("Background process started")

        flow = self.config.get("flow", [])

        sub_flow_definition = FlowDefinition(
            **{
                "key": "invoke_async",
                "session_id": self.flow_definition.session_id,
                "context": self.flow_definition.context,
                "flow": flow,
            }
        )

        # start the sub-flow asynchronously
        asyncio.create_task(self.invoke(sub_flow_definition))
        # suspend for a moment to allow the sub-flow to start
        await asyncio.sleep(0)

        self.log("Background process completed")

        return self.continue_flow()
