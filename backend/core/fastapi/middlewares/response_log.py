import logging

from fastapi import Request
from pydantic import BaseModel, ConfigDict, Field
from starlette.datastructures import Headers
from starlette.types import Message, Receive, Scope, Send

logger = logging.getLogger(__name__)
logger.propagate = False

handler = logging.StreamHandler()
formatter = logging.Formatter("%(levelname)s:\t%(asctime)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


class ResponseInfo(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    headers: Headers | None = Field(default=None, title="Response header")
    body: str = Field(default="", title="응답 바디")
    status_code: int | None = Field(default=None, title="Status code")


class ResponseLogMiddleware:
    def __init__(self, app):
        self.app = app
        self.status_code = None
        self.headers = None

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        request = Request(scope, receive)
        response_body = []

        async def _logging_send(message: Message) -> None:
            if message["type"] == "http.response.start":
                self.status_code = message["status"]
                self.headers = message.get("headers", [])
            elif message["type"] == "http.response.body":
                if body := message.get("body"):
                    response_body.append(body)
                if not message.get("more_body", False):
                    await self.log_response(request, self.status_code, self.headers, b"".join(response_body))

            await send(message)

        await self.app(scope, receive, _logging_send)

    async def log_response(self, request: Request, status_code: int, headers: list, body: bytes):
        content_type = next(
            (v.decode() for k, v in headers if k.decode().lower() == "content-type"),
            None,
        )
        log_msg = f"""
Request: {request.method} {request.url}
Status Code: {status_code}
Headers: {dict(headers)}
Content-Type: {content_type}
Body: {body[:200].decode('utf-8', errors='replace')}...
"""
        logger.info(log_msg)
