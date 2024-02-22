# Copyright (c) Microsoft. All rights reserved.

import json

from node_engine.libs.azure_openai_chat_completion import AzureOpenAIChatCompletion
from node_engine.libs.storage import Storage
from node_engine.libs.telemetry import Timer
from node_engine.libs.node_engine_component import NodeEngineComponent
from node_engine.models.flow_step import FlowStep


class ExtractMemories(NodeEngineComponent):
    description = "Extract memories from the chat history.  The output will be a list of generated memories for use in semantic search and suitable for future context building."

    default_config = {
        "service": "AZUREOPENAI_CHATCOMPLETION_GPT35",
        "prompts": [
            {
                "role": "user",
                "content": "Extract memories from the provided chat history.  The output should be a list of memories, each of which is a single sentence that describes a single event that happened in the past.  The memories should be understandable outside of the context of the chat history, in a way that will be useful for creating an embedding for semantic search.",
            },
            {
                "role": "system",
                "content": 'Use the following response format and do not provide any additional information, markup, or commentary - it is ok if there are no relevant memories, just return an empty array: {"memories": [{ "label": string, "details": string }]}',
            },
        ],
    }

    reads_from = {
        "context": None,
        "config": {
            "service": {
                "type": "string",
                "description": "The service to use for extracting the memories.",
                "required": False,
            },
            "prompts": {
                "type": [
                    {
                        "role": "string",
                        "content": "string",
                    }
                ],
                "description": "The prompts to define the types of memories to extract.",
                "required": False,
            },
            "target": {
                "type": "string",
                "description": "The key in the context where the memories will be stored.  Defaults to 'memories'.",
                "required": False,
            },
        },
    }

    writes_to = {
        "context": {
            "memories": {
                "type": "list",
                "description": "The memories extracted from the chat history.",
            }
        }
    }

    azure_openai_chat_completion = AzureOpenAIChatCompletion()

    async def execute(self) -> FlowStep:
        # store memories in database

        self.log("Extracting memories")

        messages = []

        history = await Storage.get(self.flow_definition.session_id, "messages") or []

        history_text = ""
        # last 40 messages
        for message in history[-40:]:
            history_text += f"{message['sender']}: {message['content']}\n"

        messages.append(
            {
                "role": "system",
                "content": f"<CHAT_HISTORY>{history_text}</CHAT_HISTORY>",
            }
        )

        for message in self.config.get("prompts") or []:
            messages.append({"role": message["role"], "content": message["content"]})

        service = self.config.get("service") or self.default_config["service"]

        self.log.debug({"messages": messages})

        timer = Timer()
        response = await self.azure_openai_chat_completion.create(messages, service)
        timer.stop()
        await self.telemetry.capture_average(
            "avg_chat_completion", timer.elapsed_time()
        )
        await self.telemetry.capture_average(
            "avg_chat_completion_length", len(response)
        )

        if response.startswith("Error:"):
            return self.exit_flow_with_error(response)

        data = json.loads(response)

        target = self.config.get("target", "messages")
        existing_memories = self.context.get(target, [])
        if not isinstance(existing_memories, list):
            existing_memories = [existing_memories]
        existing_memories.extend(data["memories"])
        self.context.set(target, existing_memories)

        self.log(f"memories: [{service}] {json.dumps(data['memories'])}")

        return self.continue_flow()
