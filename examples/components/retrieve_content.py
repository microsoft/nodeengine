# Copyright (c) Microsoft. All rights reserved.

from node_engine.libs.storage import Storage
from node_engine.models.node_engine_component import NodeEngineComponent
from node_engine.models.flow_step import FlowStep


class RetrieveContent(NodeEngineComponent):
    description = "Retrieves content from persistent storage."

    reads_from = {
        "context": None,
        "config": {
            "key": {
                "type": "string",
                "description": "The key for the content to retrieve from storage.",
                "required": True,
            },
            "target": {
                "type": "string",
                "description": "The key in the context to store the retrieved content.  Defaults to 'key'.",
                "required": False,
            },
            "overwrite": {
                "type": "boolean",
                "description": "Whether to overwrite the target in the context if it already exists.  Defaults to False, which will append the retrieved content to the existing content.",
                "required": False,
            },
        },
    }

    writes_to = {
        "context": {
            "some_key": {
                "type": "list",
                "description": "The retrieved content.",
            }
        }
    }

    sample_input = {
        "key": "sample",
        "session_id": "123456",
        "flow": [
            {
                "key": "start",
                "name": "RetrieveContent",
                "config": {
                    "key": "messages",
                    "target": "messages",
                    "overwrite": True,
                },
            },
        ],
    }

    sample_output = {
        "key": "sample",
        "session_id": "123456",
        "context": {
            "messages": [
                {
                    "sender": "user",
                    "content": "Hello, how are you?",
                },
            ],
        },
        "flow": [
            {
                "key": "start",
                "name": "RetrieveContent",
                "config": {
                    "key": "messages",
                    "target": "messages",
                    "overwrite": True,
                },
            },
        ],
    }

    async def execute(self) -> FlowStep:
        # Retrieve content from persistent storage.
        storage_key = self.config.get("key")
        if not storage_key:
            return self.exit_flow_with_error("No key provided in context, exiting")
        target = self.config.get("target", storage_key)
        self.log(f"Retrieving '{storage_key}' content from database.")
        content = await Storage.get(self.flow_definition.session_id, storage_key) or []

        if self.config.get("overwrite", False):
            self.context.set(target, content)
        else:
            existing_data = self.context.get(target, [])
            self.context.set(target, existing_data + content)

        self.log(f"Retrieved '{storage_key}' content from database.")

        return self.continue_flow()
