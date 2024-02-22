# Copyright (c) Microsoft. All rights reserved.

from typing import Dict, List, Literal, Optional, Union

from openai import AsyncAzureOpenAI
from openai._types import NOT_GIVEN
from openai.types.chat import (
    ChatCompletion,
    ChatCompletionMessageParam,
    ChatCompletionToolChoiceOptionParam,
    ChatCompletionToolParam,
    completion_create_params,
)

from node_engine.libs.utility import load_azureopenai_config

api_version_default = "2023-05-15"


class AzureOpenAIChatCompletion:
    async def create(
        self,
        messages: list[ChatCompletionMessageParam],
        service: str,
        max_retries: int = 2,
        retry_delay_ms: int = 1000,
        model: Optional[str] | None = None,
        endpoint: Optional[str] | None = None,
        api_key: Optional[str] | None = None,
        api_version: Optional[str] | None = None,
        frequency_penalty: Optional[float] | None = None,
        function_call: completion_create_params.FunctionCall | None = None,
        functions: List[completion_create_params.Function] | None = None,
        logit_bias: Optional[Dict[str, int]] | None = None,
        max_tokens: Optional[int] | None = None,
        n: Optional[int] | None = None,
        presence_penalty: Optional[float] | None = None,
        response_format: completion_create_params.ResponseFormat | None = None,
        seed: Optional[int] | None = None,
        stop: Union[Optional[str], List[str]] | None = None,
        stream: Optional[Literal[False]] | None = None,
        temperature: Optional[float] | None = None,
        tool_choice: ChatCompletionToolChoiceOptionParam | None = None,
        tools: List[ChatCompletionToolParam] | None = None,
        top_p: Optional[float] | None = None,
        user: str | None = None,
    ) -> str:
        # read from config, for local dev read env if not in config
        service_dict = load_azureopenai_config(service)
        model = model or service_dict["deployment"]
        endpoint = endpoint or service_dict["endpoint"]
        api_key = api_key or service_dict["key"]
        api_version = api_version or api_version_default
        client = AsyncAzureOpenAI(
            azure_endpoint=endpoint,
            azure_deployment=model,
            api_key=api_key,
            api_version=api_version,
        )

        def make_none_not_give(value):
            if value is None:
                return NOT_GIVEN
            return value

        try:
            # bug: https://github.com/openai/openai-python/issues/779
            # can't call with_options() on AsyncAzureOpenAI
            # response = await self.client.with_options(
            #    max_retries=max_retries,
            # )
            response = await client.with_options(
                max_retries=make_none_not_give(max_retries),
                timeout=make_none_not_give(retry_delay_ms),
            ).chat.completions.create(
                messages=messages,
                model=model,
                frequency_penalty=make_none_not_give(frequency_penalty),
                function_call=make_none_not_give(function_call),
                functions=make_none_not_give(functions),
                logit_bias=make_none_not_give(logit_bias),
                max_tokens=make_none_not_give(max_tokens),
                n=make_none_not_give(n),
                presence_penalty=make_none_not_give(presence_penalty),
                response_format=make_none_not_give(response_format),
                seed=make_none_not_give(seed),
                stop=make_none_not_give(stop),
                temperature=make_none_not_give(temperature),
                stream=make_none_not_give(stream),
                tool_choice=make_none_not_give(tool_choice),
                tools=make_none_not_give(tools),
                top_p=make_none_not_give(top_p),
                user=make_none_not_give(user),
            )
        except Exception as exception:
            raise Exception("Error creating chat completion.") from exception

        if not isinstance(response, ChatCompletion):
            return f"unexpected response from Azure OpenAI chat completion: {response}"

        choice = list(response.choices)[0]
        if choice.finish_reason != "stop":
            return f"incomplete response - reason: {choice.finish_reason}"

        return choice.message.content or ""
