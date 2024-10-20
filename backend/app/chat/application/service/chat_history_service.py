from app.chat.domain.entity.chat_history import ChatHistoryMessage, ChatHistoryRead
from app.chat.domain.repository.chat_history import IChatHistoryRepo


class ChatHistoryService:
    """히스토리 관리를 위한 서비스
    첫 입력과 마지막 출력을 저장하고, 이를 다음 이터레이션에 활용합니다."""

    def __init__(self, chat_history_repository: IChatHistoryRepo):
        self._chat_history_repository = chat_history_repository
        self.chat_history_messages: list[ChatHistoryMessage] = []

    async def load_chat_histories(self, session_id: str, n: int | None = None) -> None:
        history = await self._chat_history_repository.get_by_session_id(session_id)
        if history:
            if n:
                self.chat_history_messages = history.messages[-n:]
            else:
                self.chat_history_messages = history.messages

    async def update_chat_history(
        self,
        session_id: str,
        role: str,
        content: str | list[dict],
        context: dict = None,
        tool_call_id: str = None,
        name: str = None,
    ) -> None:
        self.chat_history_messages.append(
            ChatHistoryMessage(
                role=role,
                content=content,
                context=context,
                tool_call_id=tool_call_id,
                name=name,
            )
        )
        chat_history = ChatHistoryRead(session_id=session_id, messages=self.chat_history_messages)
        await self._chat_history_repository.upsert(chat_history)
