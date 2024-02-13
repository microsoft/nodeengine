# Copyright (c) Microsoft. All rights reserved.

import asyncio
import json

from openai import APIConnectionError, AsyncAzureOpenAI
from openai.types import CreateEmbeddingResponse

from node_engine.libs.utility import load_azureopenai_config

api_version = "2023-05-15"


class AzureOpenAIEmbeddings:
    async def create(
        self,
        input: str | list[str],
        azureopenai_env_var: str,
        max_retries: int = 2,
        retry_delay_ms: int = 1000,
    ) -> list[list[float]]:
        config = load_azureopenai_config(azureopenai_env_var)
        model = config["deployment"]
        client = AsyncAzureOpenAI(
            azure_endpoint=config["endpoint"],
            azure_deployment=model,
            api_key=config["key"],
            api_version=api_version,
        )

        async def retry() -> list[list[float]]:
            await asyncio.sleep(retry_delay_ms / 1000)
            return await self.create(
                input, azureopenai_env_var, max_retries - 1, retry_delay_ms * 2
            )

        # determine if text is a string or list of strings
        if isinstance(input, str):
            input = [input]

        values = []
        for item in input:
            if not isinstance(item, str):
                item = json.dumps(item)
            try:
                # bug: https://github.com/openai/openai-python/issues/779
                # can't call with_options() on AsyncAzureOpenAI
                # response = await self.client.with_options(
                #    max_retries=max_retries,
                # )
                response = await client.embeddings.create(
                    model=model,
                    input=item,
                )
            except APIConnectionError as exception:
                if max_retries > 0:
                    response = await retry()
                else:
                    raise Exception(f"Error creating chat completion: {exception}")
            except Exception as exception:
                raise Exception(f"Error creating embeddings: {exception}")

            if not isinstance(response, CreateEmbeddingResponse):
                raise Exception(
                    f"Unexpected response from Azure OpenAI embeddings: {response}"
                )

            values.append(response.data[0].embedding)

        return values
