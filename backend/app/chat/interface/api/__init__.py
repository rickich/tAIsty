from fastapi import APIRouter

from app.chat.interface.api.v1.router import router as chat_v1_router

router = APIRouter()
router.include_router(chat_v1_router, prefix="/api/v1", tags=["Chat"])


__all__ = ["router"]
