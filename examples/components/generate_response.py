# Copyright (c) Microsoft. All rights reserved.

import re
import time
from datetime import datetime

from node_engine.libs.azure_openai_chat_completion import AzureOpenAIChatCompletion
from node_engine.libs.storage import Storage
from node_engine.libs.telemetry import Timer
from node_engine.libs.node_engine_component import NodeEngineComponent
from node_engine.models.flow_step import FlowStep


class GenerateResponse(NodeEngineComponent):
    description = "Generates a response to the last message. The response will be stored in context under the key 'response' by default."

    default_config = {
        "service": "AZUREOPENAI_CHATCOMPLETION_GPT35",
        "prompts": [
            {
                "role": "system",
                "content": "Provide a response to the last message. If it appears the last message was intended for another user, send {{silence}} as the assistant response.\n\nIf the response requires information that is not available from the chat history or the provided context, either admit that you don't know the answer or ask for more information from the user. Do not make up or assume information that is not supported by evidence. Be honest and respectful in your communication.",
            }
        ],
    }

    reads_from = {
        "context": {
            "intent": {
                "type": "string",
                "description": "The intent extracted from the recent messages.",
                "required": False,
            },
            "agent": {
                "type": {
                    "id": "string",
                    "name": "string",
                    "description": "string",
                },
                "description": "The agent selected for the given user intent.",
                "required": False,
            },
        },
        "config": {
            "service": {
                "type": "string",
                "description": "The service to use for generating the response.",
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
            "target": {
                "type": "string",
                "description": "The key in the context where the response will be stored.  Defaults to 'response'.",
                "required": False,
            },
            "include_debug": {
                "type": "boolean",
                "description": "Whether to include debug information in the response.",
                "required": False,
            },
        },
    }

    writes_to = {
        "context": {
            "response": {
                "type": "string",
                "description": "The response generated from the recent messages.",
            }
        }
    }

    sample_input = {
        "key": "sample",
        "session_id": "123456",
        "context": {
            "intent": "greeting",
            "agent": {
                "id": "agent",
                "name": "Agent",
                "description": "Agent is a virtual assistant that can help you with your questions.",
            },
        },
        "flow": [
            {
                "key": "start",
                "name": "GenerateResponse",
                "config": {
                    "service": "gpt-35-turbo",
                    "prompts": [
                        {
                            "role": "system",
                            "content": "Provide a response to the last message. If it appears the last message was intended for another user, send {{silence}} as the assistant response.\n\nIf the response requires information that is not available from the chat history or the provided context, either admit that you don't know the answer or ask for more information from the user. Do not make up or assume information that is not supported by evidence. Be honest and respectful in your communication.",
                        }
                    ],
                    "target": "response",
                    "include_debug": True,
                },
            }
        ],
    }

    sample_output = {
        "key": "sample",
        "session_id": "123456",
        "context": {
            "response": {
                "content": "Hello, how are you?",
                "sender": "Agent",
                "timestamp": 1621439408,
                "debug": {
                    "completion_request": [
                        {
                            "role": "system",
                            "content": "<INTENT>greeting</INTENT>",
                        },
                        {
                            "role": "system",
                            "content": "<ASSISTANT_DESCRIPTION>Agent is a virtual assistant that can help you with your questions.</ASSISTANT_DESCRIPTION>",
                        },
                        {
                            "role": "assistant",
                            "content": "[05/19/2021, 10:30:08 PM - Agent]: Hello, how are you?",
                        },
                        {
                            "role": "system",
                            "content": "Provide a response to the last message. If it appears the last message was intended for another user, send {{silence}} as the assistant response.\n\nIf the response requires information that is not available from the chat history or the provided context, either admit that you don't know the answer or ask for more information from the user. Do not make up or assume information that is not supported by evidence. Be honest and respectful in your communication.",
                        },
                    ],
                    "completion_response": "[05/19/2021, 10:30:08 PM - Agent]: Hello, how are you?",
                },
            },
            "intent": "greeting",
            "agent": {
                "id": "agent",
                "name": "Agent",
                "description": "Agent is a virtual assistant that can help you with your questions.",
            },
        },
        "flow": [
            {
                "key": "start",
                "name": "GenerateResponse",
                "config": {
                    "service": "AZUREOPENAI_CHATCOMPLETION_GPT35",
                    "prompts": [
                        {
                            "role": "system",
                            "content": "Provide a response to the last message. If it appears the last message was intended for another user, send {{silence}} as the assistant response.\n\nIf the response requires information that is not available from the chat history or the provided context, either admit that you don't know the answer or ask for more information from the user. Do not make up or assume information that is not supported by evidence. Be honest and respectful in your communication.",
                        }
                    ],
                    "target": "response",
                },
            }
        ],
    }

    azure_openai_chat_completion = AzureOpenAIChatCompletion()

    async def execute(self) -> FlowStep:
        messages = []

        intent = self.context.get("intent")
        if intent:
            messages.append(
                {
                    "role": "system",
                    "content": f"<INTENT>{intent}</INTENT>",
                }
            )

        whiteboard_items = await Storage.get(
            self.flow_definition.session_id, "whiteboard"
        )
        if whiteboard_items:
            whiteboard_content = whiteboard_items[-1]["content"]
            messages.append(
                {
                    "role": "system",
                    "content": f"<WHITEBOARD>{whiteboard_content}</WHITEBOARD>",
                }
            )

        agent = self.config.get("agent") or self.context.get("agent")
        if agent:
            messages.append(
                {
                    "role": "system",
                    "content": f"<ASSISTANT_DESCRIPTION>{agent['description']}</ASSISTANT_DESCRIPTION>",
                }
            )
        else:
            agent = {
                "id": "agent",
                "name": "Agent",
            }

        storage_key = self.config.get("storage_key", "messages")
        history = await Storage.get(self.flow_definition.session_id, storage_key) or []
        # last 40 messages
        for message in history[-40:]:
            if "timestamp" not in message:
                message["timestamp"] = int(time.time())
            messages.append(
                {
                    "role": (
                        "assistant" if message["sender"] == agent["name"] else "user"
                    ),
                    "content": "[{timestamp} - {sender}]: {content}".format(
                        timestamp=format_timestamp(message["timestamp"]),
                        sender=message["sender"],
                        content=message["content"],
                    ),
                }
            )

        for message in self.config.get("prompts") or []:
            messages.append({"role": message["role"], "content": message["content"]})
        self.log.debug({"messages": messages})

        timer = Timer()
        service = self.config.get("service") or self.default_config["service"]
        completion = await self.azure_openai_chat_completion.create(messages, service)
        timer.stop()
        await self.telemetry.capture_average(
            "avg_chat_completion", timer.elapsed_time()
        )
        await self.telemetry.capture_average(
            "avg_chat_completion_length", len(completion)
        )

        # strip the name of the agent from the response
        response = completion
        if response.startswith("["):
            response = re.sub(r"\[.*\]:\s", "", response)

        response_message = {
            "sender": agent["name"],
            "timestamp": int(time.time()),
            "content": response,
        }

        if self.config.get("include_debug"):
            response_message["debug"] = {
                "completion_service": service,
                "completion_request": messages,
                "completion_response": completion,
            }

        target = self.config.get("target", "messages")
        existing_content = self.context.get(target, [])
        if not isinstance(existing_content, list):
            existing_content = [existing_content]
        existing_content.append(response_message)
        self.context.set(target, existing_content)

        self.context.set("response", response_message)

        self.log(f"Response generated [{service}]: {response}.")

        return self.continue_flow()


def format_timestamp(timestamp: int):
    # return format: 1/1/2023, 12:00:00 AM
    return datetime.fromtimestamp(timestamp).strftime("%m/%d/%Y, %I:%M:%S %p")
