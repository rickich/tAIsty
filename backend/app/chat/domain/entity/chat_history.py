from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Column, String, Text

from core.db.mixins import TimestampMixin
from core.db.session import Base


class ChatHistory(Base, TimestampMixin):
    __tablename__ = "chat_history"

    id = Column(String, primary_key=True, index=True)
    session_id = Column(String)
    messages = Column(Text)


class ChatHistoryMessage(BaseModel):
    message_id: str = Field(default_factory=lambda: str(uuid4()))
    role: str
    content: str | list[dict]
    context: dict | None = (
        None  # chaining의 경우 context에 전 단계의 llm의 input/output을 저장하여 다음 call에 활용할 수 있습니다.
    )
    tool_call_id: str | None = None
    name: str | None = None


class ChatHistoryRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str = Field(default_factory=lambda: str(uuid4()))
    session_id: str
    messages: list[ChatHistoryMessage]
