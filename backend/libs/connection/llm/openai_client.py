import json
from collections.abc import AsyncGenerator
from typing import Literal

from openai import AsyncOpenAI, AsyncStream
from openai.types.chat import ChatCompletion, ChatCompletionChunk

from libs.connection.llm.interface import ILLMClient


class OpenAIClient(ILLMClient):
    def __init__(
        self,
        api_key: str,
        endpoint: str,
        model: str = "gpt-4o",
        max_tokens: int = 300,
        temperature: float = 0,
        top_p: float = 1,
    ):
        self._async_client = AsyncOpenAI(api_key=api_key, base_url=endpoint)
        self._default_model = model
        self._default_params = {
            "max_tokens": max_tokens,
            "temperature": temperature,
            "top_p": top_p,
        }

    async def generate(
        self,
        chat_messages: list[dict[str, any]],
        system_prompt: str | None = None,
        model: str | None = None,
        **kwargs,
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if chat_messages:
            messages.extend(chat_messages)

        params = {**self._default_params, **kwargs}

        response: ChatCompletion = await self._async_client.chat.completions.create(
            model=model or self._default_model,
            messages=messages,
            **params,
        )
        return response.choices[0].message.content.strip()

    async def generate_stream(
        self,
        chat_messages: list[dict[str, any]],
        system_prompt: str | None = None,
        tools: list[dict] | None = None,
        tool_choice: Literal["none", "auto", "required"] = "auto",
        model: str | None = None,
        **kwargs,
    ) -> AsyncGenerator[str | list[dict], None]:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        if chat_messages:
            messages.extend(chat_messages)

        create_args = {
            "model": model or self._default_model,
            "messages": messages,
            "stream": True,
            **self._default_params,
            **kwargs,
        }
        if tools:
            create_args.update({"tools": tools, "tool_choice": tool_choice})

        subscription: AsyncStream[ChatCompletionChunk] = await self._async_client.chat.completions.create(**create_args)

        tool_calls = []

        function_name = ""
        function_arguments_str = ""
        tool_call_id = None
        async for chunk in subscription:
            if not chunk.choices:
                continue

            message = chunk.choices[0].delta
            if message.tool_calls:
                if message.tool_calls[0].id:
                    if function_arguments_str and message.tool_calls[0].id != tool_call_id:
                        tool_calls.append(
                            {
                                "type": "tool_call",
                                "tool_call_id": tool_call_id,
                                "function_name": function_name,
                                "function_arguments": json.loads(function_arguments_str),
                            }
                        )
                        function_arguments_str = ""

                    tool_call_id = message.tool_calls[0].id
                    function_name = message.tool_calls[0].function.name

                function_arguments_str += message.tool_calls[0].function.arguments
            else:
                if message.content:
                    yield message.content

            if chunk.choices[0].finish_reason == "tool_calls":
                tool_calls.append(
                    {
                        "type": "tool_call",
                        "tool_call_id": tool_call_id,
                        "function_name": function_name,
                        "function_arguments": json.loads(function_arguments_str),
                    }
                )

                yield tool_calls
