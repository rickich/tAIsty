from typing import Any

from jinja2 import BaseLoader, Environment, StrictUndefined, meta
from pydantic import BaseModel

from libs.service.llm import (
    BaseContent,
    ChatMessage,
    ImageUrlContent,
    ImageUrlData,
    TextContent,
)
from libs.service.prompt.exceptions import PromptCompileError


class Prompt(BaseModel):
    name: str  # prompt name
    parameters: dict[str, Any]  # prompt parameters
    messages: list[ChatMessage]  # not compiled chat messages

    def compile(self, **kwargs) -> list[ChatMessage]:
        compiled_messages = []

        for message in self.messages:
            compiled_content = self._compile(message.content, kwargs)
            compiled_messages.append(ChatMessage(role=message.role, content=compiled_content))

        return compiled_messages

    @staticmethod
    def get_system_prompt(messages: list[ChatMessage]) -> str | None:
        for message in messages:
            if message.role == "system":
                return message.content
        return None

    @staticmethod
    def get_chat_messages(messages: list[ChatMessage]) -> list[ChatMessage]:
        return [message for message in messages if message.role != "system"]

    @staticmethod
    def _compile(content: str | list[BaseContent], data: dict[str, Any]) -> str | list[BaseContent]:

        if not isinstance(content, str | list):
            raise ValueError("Content must be a string or a list of BaseContent")

        if isinstance(content, list):
            compiled_content = []
            for item in content:
                if isinstance(item, TextContent):
                    compiled_content.append(
                        TextContent(
                            type=item.type,
                            text=Prompt._compile_template_string(item.text, data),
                        )
                    )
                elif isinstance(item, ImageUrlContent):
                    compiled_content.append(
                        ImageUrlContent(
                            type=item.type,
                            image_url=ImageUrlData(
                                url=Prompt._compile_template_string(item.image_url.url, data),
                            ),
                        )
                    )
                else:
                    raise ValueError(f"Unsupported content type: {type(item)} in {item}")

            return compiled_content

        return Prompt._compile_template_string(content, data)

    @staticmethod
    def _compile_template_string(content: str, data: dict[str, Any]) -> str:
        env = Environment(loader=BaseLoader(), undefined=StrictUndefined)
        template = env.from_string(content)

        # Extract variables from template
        parsed_content = env.parse(content)
        variables = meta.find_undeclared_variables(parsed_content)

        # Check if all variables are provided
        missing_variables = variables - set(data.keys())
        if missing_variables:
            raise PromptCompileError(f"Variables in template not provided in data: {missing_variables}")

        return template.render(data)
