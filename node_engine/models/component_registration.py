# Copyright (c) Microsoft. All rights reserved.

from node_engine.models.node_engine_base_model import NodeEngineBaseModel

# Samples of component registration:

# {
#     "key": "component_key",
#     "label": "component_label",
#     "description": "component_description",
#     "type": "service",
#     "config": {
#         "endpoint": "http://localhost:8000/api/v1/flow/execute",
#     },
# }

# {
#     "key": "component_key",
#     "label": "component_label",
#     "description": "component_description",
#     "type": "code",
#     "config": {
#         "import time\nimport re\nfrom datetime import datetime\nfrom node_engine.libs.azure_openai_chat_completion import AzureOpenAIChatCompletion\nfrom node_engine.libs.log import Log\nfrom node_engine.libs.context import Context\nfrom node_engine.libs.config import ComponentConfig\nfrom node_engine.models.flow_definition import FlowDefinition\nfrom node_engine.libs.storage import Storage\nfrom node_engine.libs.telemetry import Telemetry, Timer\n\n# Sample usage\n# {\n#     \"key\": \"sample\",\n#     \"session_id\": \"123456\",\n#     \"context\": {\n#         \"messages\": [\n#             {\n#                 \"sender\": \"user\",\n#                 \"timestamp\": 1629386400,\n#                 \"content\": \"Hello\",\n#             }\n#         ],\n#         \"intent\": \"greeting\",\n#     },\n#     \"flow\": [\n#         {\n#             \"key\": \"start\",\n#             \"name\": \"GenerateResponse\",\n#             \"config\": {\n#                 \"model\": \"gpt-35-turbo\",\n#                 \"prompts\": [\n#                     {\n#                         \"role\": \"system\",\n#                         \"content\": \"Provide a response to the last message. If it appears the last message was intended for another user, send {{silence}} as the assistant response.\\n\\nIf the response requires information that is not available from the chat history or the provided context, either admit that you don't know the answer or ask for more information from the user. Do not make up or assume information that is not supported by evidence. Be honest and respectful in your communication.\",\n#                     }\n#                 ],\n#             },\n#             \"outputs\": {\n#                 \"next\": \"exit\",\n#             },\n#         }\n#     ],\n# }\n\ndefault_config = {\n    \"model\": \"gpt-35-turbo\",\n    \"prompts\": [\n        {\n            \"role\": \"system\",\n            \"content\": \"Provide a response to the last message. If it appears the last message was intended for another user, send {{silence}} as the assistant response.\\n\\nIf the response requires information that is not available from the chat history or the provided context, either admit that you don't know the answer or ask for more information from the user. Do not make up or assume information that is not supported by evidence. Be honest and respectful in your communication.\",\n        }\n    ],\n}\n\n\nclass GenerateResponse:\n    azure_openai_chat_completion = AzureOpenAIChatCompletion()\n\n    async def execute(self, flow_definition: FlowDefinition, component_key: str):\n        # generate response from intent\n\n        log = Log(\"generate_response\", flow_definition)\n        context = Context(flow_definition)\n        config = ComponentConfig(\n            flow_definition, component_key, default_config\n        )\n\n        log(\"Generating response\")\n\n        messages = []\n\n        intent = context.get(\"intent\")\n        if intent:\n            messages.append(\n                {\n                    \"role\": \"system\",\n                    \"content\": \"<INTENT>{}</INTENT>\".format(intent),\n                }\n            )\n\n        agent = context.get(\"agent\")\n        if agent:\n            messages.append(\n                {\n                    \"role\": \"system\",\n                    \"content\": \"<ASSISTANT_DESCRIPTION>{}</ASSISTANT_DESCRIPTION>\".format(\n                        agent[\"description\"]\n                    ),\n                }\n            )\n        else:\n            agent = {\n                \"id\": \"agent\",\n                \"name\": \"Agent\",\n            }\n\n        history = await Storage.get(flow_definition.session_id, \"messages\") or []\n        for message in history:\n            messages.append(\n                {\n                    \"role\": \"assistant\"\n                    if message[\"sender\"] == agent[\"name\"]\n                    else \"user\",\n                    \"content\": \"[{timestamp}] {sender}: {content}\".format(\n                        timestamp=format_timestamp(message[\"timestamp\"]),\n                        sender=message[\"sender\"],\n                        content=message[\"content\"],\n                    ),\n                }\n            )\n\n        prompts = config.get(\"prompts\")\n        for message in prompts:\n            messages.append({\"role\": message[\"role\"], \"content\": message[\"content\"]})\n\n        model = config.get(\"model\")\n\n        log.debug({\"messages\": messages})\n\n        telemetry = Telemetry(\n            flow_definition.session_id, flow_definition.key, component_key\n        )\n        timer = Timer()\n        completion = await self.azure_openai_chat_completion.create(messages, model)\n        timer.stop()\n        await telemetry.capture_average(\"avg_chat_completion\", timer.elapsed_time())\n        await telemetry.capture_average(\"avg_chat_completion_length\", len(completion))\n\n        # strip the name of the agent from the response\n        response = completion\n        if response.startswith(\"[\"):\n            response = re.sub(r\"\\[.*\\].*:\\s\", \"\", response)\n\n        if \"messages\" not in flow_definition.context:\n            flow_definition.context[\"messages\"] = []\n        flow_definition.context[\"messages\"].append(\n            {\n                \"sender\": agent[\"name\"],\n                \"timestamp\": int(time.time()),\n                \"content\": response,\n            }\n        )\n\n        flow_definition.context[\"output\"] = response\n\n        log(\n            \"Response generated [{model}]: {response}\".format(\n                model=model, response=response\n            )\n        )\n\n        return {\n            \"flow_definition\": flow_definition,\n            \"next\": None,\n        }\n\n\ndef format_timestamp(timestamp: int):\n    # return format: 1/1/2023, 12:00:00 AM\n    return datetime.fromtimestamp(timestamp).strftime(\"%m/%d/%Y, %I:%M:%S %p\")\n",
#     },
# }

# {
#     "key": "component_key",
#     "label": "component_label",
#     "description": "component_description",
#     "type": "module",
#     "config": {
#         "module": "node_engine.components.store_content",
#         "class": "StoreContent",
#     },
# }


class ComponentRegistration(NodeEngineBaseModel):
    key: str
    label: str
    description: str
    type: str
    config: dict
