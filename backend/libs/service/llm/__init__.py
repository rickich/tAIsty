from typing import Literal

from pydantic import BaseModel
from pydantic.dataclasses import dataclass


@dataclass
class ImageUrlData:
    url: str


class BaseContent(BaseModel):
    type: Literal["text", "image_url"]


class TextContent(BaseContent):
    text: str


class ImageUrlContent(BaseContent):
    image_url: ImageUrlData


class ChatMessage(BaseModel):
    role: str
    content: str | list[TextContent | ImageUrlContent]
