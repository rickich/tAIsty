from abc import abstractmethod

from app.chat.domain.entity.chat_history import ChatHistory, ChatHistoryRead
from libs.repository.interface import IBaseRepo


class IChatHistoryRepo(IBaseRepo[ChatHistory, ChatHistoryRead]):
    @abstractmethod
    async def upsert(self, schema: ChatHistoryRead) -> None:
        pass

    @abstractmethod
    async def get_by_session_id(self, session_id: str) -> ChatHistory | None:
        pass
