import json

from sqlalchemy import select

from app.chat.domain.entity.chat_history import ChatHistory, ChatHistoryRead
from app.chat.domain.repository.chat_history import IChatHistoryRepo
from core.db.session import session_factory
from libs.repository.rdb_base_repo import RDBBaseRepo


class RDBChatHistoryRepo(RDBBaseRepo[ChatHistory, ChatHistoryRead], IChatHistoryRepo):
    def __init__(self):
        super().__init__(ChatHistory, ChatHistoryRead)

    def to_schema(self, model: ChatHistory) -> ChatHistoryRead:
        schema = ChatHistoryRead(
            session_id=model.session_id,
            messages=json.loads(model.messages),
        )
        if model.id:
            schema.id = model.id
        return schema

    async def upsert(self, schema: ChatHistoryRead) -> ChatHistoryRead:
        async with session_factory() as session:
            query = select(ChatHistory).where(ChatHistory.session_id == schema.session_id)
            result = await session.execute(query)
            item = result.scalars().first()

            messages = json.dumps([message.model_dump(mode="json") for message in schema.messages])
            if item:
                item.messages = messages
            else:
                item = ChatHistory(id=schema.id, session_id=schema.session_id, messages=messages)

                session.add(item)

            await session.commit()
            await session.refresh(item)

        return self.to_schema(item)

    async def get_by_session_id(self, session_id: str) -> ChatHistoryRead | None:
        async with session_factory() as session:
            query = select(self.model).where(self.model.session_id == session_id)
            result = await session.execute(query)
        item = result.scalars().first()
        return self.to_schema(item) if item else None
