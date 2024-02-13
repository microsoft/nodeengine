# Copyright (c) Microsoft. All rights reserved.

from node_engine.libs.azure_openai_embeddings import AzureOpenAIEmbeddings
from node_engine.models.node_engine_component import NodeEngineComponent
from node_engine.models.flow_step import FlowStep


class ExtractEmbeddings(NodeEngineComponent):
    description = "Extract embeddings from text. Pass the text in the context and the embeddings will be returned in the context."

    default_config = {"service": "AZUREOPENAI_EMBEDDINGS"}

    reads_from = {
        "context": "as defined in config",
        "config": {
            "source": {
                "type": "string",
                "description": "The key in the context containing the text to be embedded.",
                "required": True,
            },
            "target": {
                "type": "string",
                "description": "The key in the context to store the embeddings.",
                "required": True,
            },
        },
    }

    writes_to = {
        "context": "as defined in config",
    }

    sample_input = {
        "key": "sample",
        "session_id": "123456",
        "context": {
            "memories": [
                "Offering help: Assistant offered help and encouraged the user to ask questions if needed."
            ],
        },
        "flow": [
            {
                "key": "start",
                "name": "ExtractEmbeddings",
                "config": {
                    "source": "memories",
                    "target": "memories_embeddings",
                },
            },
        ],
    }

    sample_output = {
        "key": "sample",
        "session_id": "123456",
        "context": {
            "memories": [
                "Offering help: Assistant offered help and encouraged the user to ask questions if needed."
            ],
            "memories_embeddings": [
                {
                    "item": "Offering help: Assistant offered help and encouraged the user to ask questions if needed.",
                    "embedding": [
                        -0.0003509521484375,
                        0.00018310546875,
                        0.0001220703125,
                    ],
                }
            ],
        },
    }

    azure_openai_embeddings = AzureOpenAIEmbeddings()

    async def execute(self) -> FlowStep:
        # extract embeddings

        self.log("Extract embeddings started")

        # get source from context
        source_key = self.config.get("source")
        if not source_key:
            return self.exit_flow_with_error("Source not found in config")
        source_data = self.context.get(source_key)
        if not source_data:
            return self.exit_flow_with_error(
                "Source '{}' not found in context".format(source_key)
            )

        # get target from context
        target_key = self.config.get("target")
        if not target_key:
            return self.exit_flow_with_error("Target not found in config")

        service = self.config.get("service") or self.default_config["service"]

        # get embeddings
        embeddings = await self.azure_openai_embeddings.create(source_data, service)

        results = []
        for i in range(len(source_data)):
            results.append({"item": source_data[i], "embedding": embeddings[i]})

        # add embeddings to context
        self.context.set(target_key, results)

        self.log("Extract embeddings completed")

        return self.continue_flow()
