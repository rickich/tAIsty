from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from contextvars import ContextVar, Token

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from core.config import config

session_context: ContextVar[str] = ContextVar("session_context")


def get_session_context() -> str:
    return session_context.get()


def set_session_context(session_id: str) -> Token:
    return session_context.set(session_id)


def reset_session_context(context: Token) -> None:
    session_context.reset(context)


class RoutingSession(Session):
    def get_bind(self, mapper=None, clause=None, **kw):
        return engine.sync_engine


engine = create_async_engine(config.db_url, echo=False, pool_pre_ping=True, pool_recycle=3600)
Base = declarative_base()


# 전역 세션 생성
_async_session_factory = async_sessionmaker(
    class_=AsyncSession,
    sync_session_class=RoutingSession,
    expire_on_commit=False,
)
session = async_scoped_session(
    session_factory=_async_session_factory,
    scopefunc=get_session_context,
)


@asynccontextmanager
async def session_factory() -> AsyncGenerator[AsyncSession, None]:
    async_session = async_sessionmaker(
        class_=AsyncSession,
        bind=engine,
        expire_on_commit=False,
    )()
    try:
        yield async_session
    except Exception:
        await async_session.rollback()
        raise
    finally:
        await async_session.close()
