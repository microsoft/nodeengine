# Copyright (c) Microsoft. All rights reserved.

import asyncio

from node_engine.models.flow_definition import FlowDefinition
from node_engine.models.node_engine_component import NodeEngineComponent
from node_engine.models.flow_step import FlowStep

invoke_url = "http://localhost:8000/invoke"


class ProcessMemories(NodeEngineComponent):
    definition = "Perform processing of memories for a given set of messages."

    reads_from = {
        "context": {
            "messages": {
                "type": "list",
                "description": "List of messages to process.",
                "required": True,
            }
        },
        "config": {
            "await": {
                "type": "boolean",
                "description": "Whether to await the sub-flow or not.",
                "default": True,
            },
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
                "name": "ProcessMemories",
                "config": {
                    "await": False,
                },
            },
        ],
    }

    async def execute(self) -> FlowStep:
        # process memories

        self.log("Process memories started")

        messages = self.context.get("messages", [])

        sub_flow_definition = FlowDefinition(
            **{
                "key": "process_memories",
                "session_id": self.flow_definition.session_id,
                "context": {"input": messages},
                "flow": [
                    {
                        "key": "start",
                        "name": "StoreContent",
                        "config": {
                            "source": "input",
                            "key": "content",
                        },
                    },
                    {"key": "extract_memories", "name": "ExtractMemories"},
                    {
                        "key": "store_memories",
                        "name": "StoreContent",
                        "config": {
                            "source": "memories",
                        },
                    },
                    {
                        "key": "extract_embeddings",
                        "name": "ExtractEmbeddings",
                        "config": {
                            "source": "memories",
                            "target": "memories_embeddings",
                        },
                    },
                    {
                        "key": "store_embeddings",
                        "name": "StoreContent",
                        "config": {
                            "source": "memories_embeddings",
                        },
                    },
                ],
            }
        )

        if self.config.get("await", True):
            await self.invoke(sub_flow_definition)
        else:
            # Start the task in the background
            asyncio.create_task(self.invoke(sub_flow_definition))
            # Suspend for a moment to allow the task to start
            await asyncio.sleep(0)

        return self.continue_flow()
