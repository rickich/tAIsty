from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator


class ILLMClient(ABC):
    @abstractmethod
    async def generate(
        self,
        chat_messages: list[dict[str, any]],
        system_prompt: str,
        response_format: str,
        model: str | None = None,
        **kwargs,
    ) -> str:
        pass

    @abstractmethod
    async def generate_stream(
        self,
        chat_messages: list[dict[str, any]],
        system_prompt: str,
        tools: list[dict],
        tool_choice: str,
        model: str | None = None,
        **kwargs,
    ) -> AsyncGenerator[str, None]:
        pass
