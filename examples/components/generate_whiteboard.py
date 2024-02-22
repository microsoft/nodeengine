# Copyright (c) Microsoft. All rights reserved.

import time

from node_engine.libs.azure_openai_chat_completion import AzureOpenAIChatCompletion
from node_engine.libs.storage import Storage
from node_engine.libs.telemetry import Timer
from node_engine.libs.node_engine_component import NodeEngineComponent
from node_engine.models.flow_step import FlowStep


class GenerateWhiteboard(NodeEngineComponent):
    description = "Generate whiteboard content which is a capture of important information from the conversation."

    default_config = {
        "service": "AZUREOPENAI_CHATCOMPLETION_GPT4",
        "prompts": [
            {
                "role": "user",
                "content": "Please provide updated <WHITEBOARD/> content based upon information extracted from the <CHAT_HISTORY/>. Do not provide any information that is not already in the chat history and do not answer any pending requests.",
            },
            {
                "role": "system",
                "content": "The assistant has access to look up information in the rest of the chat history, but this is based upon semantic similarity to current user request, so the whiteboard content is for information that should always be available to the bot, even if it is not directly semantically related to the current user request.\n\nThe whiteboard is limited in size, so it is important to keep it up to date with the most important information and it is ok to remove information that is no longer relevant.  It is also ok to leave the whiteboard blank if there is no information important enough be added to the whiteboard.\n\nThink of the whiteboard as the type of content that might be written down on a whiteboard during a meeting. It is not a transcript of the conversation, but rather only the most important information that is relevant to the current task at hand.\n\nUse markdown to format the whiteboard content.  For example, you can use headings, lists, and links to other resources: <WHITEBOARD>{markdown}</WHITEBOARD>\n\nJust return the <WHITEBOARD/> content.  The assistant will automatically update the whiteboard content in the context.",
            },
        ],
    }

    reads_from = {
        "context": None,
        "config": {
            "model": {
                "type": "string",
                "description": "The model to use for generating the whiteboard.",
                "required": False,
            },
            "prompts": {
                "type": [
                    {
                        "role": "string",
                        "content": "string",
                    }
                ]
            },
            "include_debug": {
                "type": "boolean",
                "description": "Whether to include debug information in the whiteboard.  Defaults to False.",
                "required": False,
            },
        },
    }

    writes_to = {
        "context": {
            "whiteboard": {
                "type": "object",
                "description": "The whiteboard content.",
            }
        },
    }

    sample_input = {
        "key": "sample",
        "session_id": "123456",
        "flow": [
            {"key": "start", "name": "GenerateWhiteboard"},
        ],
    }

    sample_output = {
        "key": "sample",
        "session_id": "123456",
        "context": {
            "whiteboard": {
                "timestamp": 1634176800,
                "content": "This is the whiteboard content.",
            },
        },
    }

    azure_openai_chat_completion = AzureOpenAIChatCompletion()

    async def execute(self) -> FlowStep:
        # generate whiteboard

        self.log("Whiteboard generation started")

        messages = []

        # add last whiteboard to messages
        whiteboard_items = await Storage.get(
            self.flow_definition.session_id, "whiteboard"
        )
        whiteboard_content = (
            whiteboard_items[-1]["content"] if whiteboard_items else "No content."
        )
        messages.append(
            {
                "role": "system",
                "content": f"<WHITEBOARD>{whiteboard_content}</WHITEBOARD>",
            }
        )

        # add chat history to messages
        history = await Storage.get(self.flow_definition.session_id, "messages") or []
        messages.append(
            {
                "role": "system",
                "content": "<CHAT_HISTORY>{chat_history}</CHAT_HISTORY>".format(
                    chat_history="\n".join(
                        [
                            "[{sender}]: {content}".format(
                                sender=message["sender"],
                                content=message["content"],
                            )
                            # last 100 messages
                            for message in history[-100:]
                        ]
                    )
                ),
            }
        )

        timestamp = history[-1]["timestamp"] if history else int(time.time())

        for prompt in self.config.get("prompts") or []:
            messages.append(prompt)

        service = self.config.get("service") or self.default_config["service"]

        self.log.debug({"messages": messages})

        timer = Timer()
        completion = await self.azure_openai_chat_completion.create(messages, service)
        timer.stop()
        await self.telemetry.capture_average(
            "avg_chat_completion", timer.elapsed_time()
        )
        await self.telemetry.capture_average(
            "avg_chat_completion_length", len(completion)
        )

        self.log.debug({"completion": completion})

        # strip the whiteboard content from the completion
        content = completion.split("<WHITEBOARD>")[1].split("</WHITEBOARD>")[0]
        whiteboard = {"timestamp": timestamp, "content": content}

        if self.config.get("include_debug"):
            whiteboard["debug"] = {
                "completion_service": service,
                "completion_request": messages,
                "completion_response": completion,
            }

        self.context.set("whiteboard", whiteboard)

        self.log("Generate whiteboard completed")

        return self.continue_flow()
