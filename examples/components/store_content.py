# Copyright (c) Microsoft. All rights reserved.

from node_engine.libs.storage import Storage
from node_engine.models.node_engine_component import NodeEngineComponent
from node_engine.models.flow_step import FlowStep


class StoreContent(NodeEngineComponent):
    description = "Stores content in persistent storage."

    reads_from = {
        "context": {
            "some_key": {
                "types": ["string", "list"],
                "description": "The content to store in storage.",
                "required": True,
            }
        },
        "config": {
            "source": {
                "type": "string",
                "description": "The key in the context where the content to store is located.",
                "required": True,
            },
            "key": {
                "type": "string",
                "description": "The key to store the content in storage. Defaults to value of 'source'.",
                "required": False,
            },
            "overwrite": {
                "type": "boolean",
                "description": "Whether to overwrite the content in storage if it already exists.  Defaults to False, which will append the content to the existing content.",
                "required": False,
            },
            "raw": {
                "type": "boolean",
                "description": "Whether to store the raw content or the parsed content.  Defaults to False, which will store the parsed content.",
                "required": False,
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
                    "content": "Hello, how are you?",
                },
            ],
        },
        "flow": [
            {
                "key": "start",
                "name": "StoreContent",
                "config": {
                    "source": "messages",
                    "key": "messages",
                    "overwrite": True,
                },
            },
        ],
    }

    async def execute(self) -> FlowStep:
        # store content in persistent storage

        source_key = self.config.get("source")
        if not source_key:
            return self.exit_flow_with_error("No source provided in context")
        source_data = self.context.get(source_key, [])

        storage_key = self.config.get("key", source_key)

        # store content in database
        self.log(f"Storing '{source_key}' content in database")

        if self.config.get("raw", False):
            await Storage.set(
                self.flow_definition.session_id, storage_key, source_data, raw=True
            )
            self.log(f"Stored '{source_key}' content in database")
            return self.continue_flow()

        if not isinstance(source_data, list):
            source_data = [source_data]

        existing_data = (
            await Storage.get(self.flow_definition.session_id, storage_key) or []
        )

        if existing_data and not self.config.get("overwrite", False):
            await Storage.set(
                self.flow_definition.session_id,
                storage_key,
                existing_data + source_data,
            )
        else:
            await Storage.set(self.flow_definition.session_id, storage_key, source_data)

        self.log(f"Stored '{source_key}' content in database")

        return self.continue_flow()
