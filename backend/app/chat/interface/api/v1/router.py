from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse

from app.chat.application.service.chatbot_service import ChatbotService
from app.chat.interface.api.v1.request import ChatRequest
from app.chat.interface.api.v1.response import ChatResponse
from app.dependency import Container
from libs.utils.img import detect_image_format

router = APIRouter()


@router.post("/stream")
@inject
async def stream(
    request: ChatRequest,
    chatbot: ChatbotService = Depends(Provide[Container.chatbot_service]),
) -> StreamingResponse:

    ext = None

    if request.image:
        # detect image format
        try:
            ext = detect_image_format(request.image)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid image")

    return StreamingResponse(
        chatbot.generate_stream_response(
            session_id=request.session_id,
            user_message=request.message,
            image_content=request.image,
            image_type=ext,
            limit=request.limit,
        ),
        media_type="text/event-stream",
    )


@router.post("/chat")
@inject
async def chat(
    request: ChatRequest,
    chatbot: ChatbotService = Depends(Provide[Container.chatbot_service]),
) -> ChatResponse:
    ext = None
    if request.image:
        # detect image format
        try:
            ext = detect_image_format(request.image)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid image")

    resp = await chatbot.generate_response(
        session_id=request.session_id,
        user_message=request.message,
        image_content=request.image,
        image_type=ext,
        limit=request.limit,
    )

    return ChatResponse(**resp)


@router.get("/ping")
async def ping():
    return {"response": "pong"}
