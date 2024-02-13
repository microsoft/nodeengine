# Copyright (c) Microsoft. All rights reserved.

import asyncio

from openai import APIConnectionError, AsyncAzureOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionMessageParam

from node_engine.libs.utility import load_azureopenai_config

api_version = "2023-05-15"


class AzureOpenAIChatCompletion:
    async def create(
        self,
        messages: list[ChatCompletionMessageParam],
        azureopenai_env_var: str,
        max_retries: int = 2,
        retry_delay_ms: int = 1000,
    ) -> str:
        config = load_azureopenai_config(azureopenai_env_var)
        model = config["deployment"]
        client = AsyncAzureOpenAI(
            azure_endpoint=config["endpoint"],
            azure_deployment=model,
            api_key=config["key"],
            api_version=api_version,
        )

        async def retry():
            await asyncio.sleep(retry_delay_ms / 1000)
            return await self.create(
                messages, azureopenai_env_var, max_retries - 1, retry_delay_ms * 2
            )

        try:
            # bug: https://github.com/openai/openai-python/issues/779
            # can't call with_options() on AsyncAzureOpenAI
            # response = await self.client.with_options(
            #    max_retries=max_retries,
            # )
            response = await client.chat.completions.create(
                model=model, messages=messages
            )
        except APIConnectionError as exception:
            if max_retries > 0:
                response = await retry()
            else:
                raise Exception(f"Error creating chat completion: {exception}")
        except Exception as exception:
            raise Exception(f"Error creating chat completion: {exception}")

        if not isinstance(response, ChatCompletion):
            return f"unexpected response from Azure OpenAI chat completion: {response}"

        choice = list(response.choices)[0]
        if choice.finish_reason != "stop":
            return f"incomplete response - reason: {choice.finish_reason}"

        return choice.message.content or ""
