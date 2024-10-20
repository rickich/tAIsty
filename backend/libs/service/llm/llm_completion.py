import asyncio
from collections.abc import AsyncGenerator

from libs.connection.llm.interface import ILLMClient
from libs.service.llm import ChatMessage


class LLMCompletionService:
    def __init__(self, client: ILLMClient):
        self._client = client

    async def run_nlp_task(
        self,
        chat_messages: list[ChatMessage] | None = None,
        system_prompt: str | None = None,
        model: str | None = None,
        **kwargs,
    ) -> str:
        return await self._client.generate(
            chat_messages=chat_messages or [],
            system_prompt=system_prompt,
            model=model,
            **kwargs,
        )

    async def run_nlp_task_stream(
        self,
        chat_messages: list[ChatMessage] | None = None,
        system_prompt: str | None = None,
        tools: list[dict] | None = None,
        tool_choice: str = "auto",
        model: str | None = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        max_retries = 3
        retry_count = 0

        while retry_count < max_retries:
            try:
                subscription = self._client.generate_stream(
                    chat_messages=chat_messages or [],
                    system_prompt=system_prompt,
                    tools=tools,
                    tool_choice=tool_choice,
                    model=model,
                    **kwargs,
                )
                async for chunk in subscription:
                    yield chunk
                return
            except Exception as e:
                print(f"Error in run_nlp_task_stream: {e}")
                retry_count += 1
                if retry_count < max_retries:
                    print(f"Retrying... ({retry_count}/{max_retries})")
                    await asyncio.sleep(3)
                else:
                    yield "Sorry, an error occurred while using the service. Please try again later."
