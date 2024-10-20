import logging

from fastapi import FastAPI, Request
from fastapi.middleware import Middleware
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.chat.interface.api import router as chat_router
from app.dependency import Container
from core.config import config
from core.db.session import Base, engine
from core.exceptions import CustomException
from core.fastapi.middlewares import ResponseLogMiddleware
from core.fastapi.middlewares.response_log import logger


def init_routers(app_: FastAPI) -> None:
    container = Container()
    container.config.from_dict(config.model_dump(mode="json"))
    app_.include_router(chat_router)


def init_listeners(app_: FastAPI) -> None:
    @app_.exception_handler(Exception)
    async def global_exception_handler(request: Request, exc: Exception):
        logger.error(f"Unhandled exception: {type(exc).__name__} - {str(exc)}")
        return JSONResponse(
            status_code=500,
            content={
                "error_code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected error occurred.",
            },
        )

    # Exception handler
    @app_.exception_handler(CustomException)
    async def custom_exception_handler(request: Request, exc: CustomException):
        return JSONResponse(
            status_code=exc.code,
            content={"error_code": exc.error_code, "message": exc.message},
        )

    @app_.on_event("startup")
    async def startup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


def make_middleware() -> list[Middleware]:
    middleware = [
        Middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        ),
        Middleware(ResponseLogMiddleware),
    ]
    return middleware


def create_app() -> FastAPI:
    logging.basicConfig(level=logging.INFO)

    app_ = FastAPI(
        middleware=make_middleware(),
    )
    init_routers(app_=app_)
    init_listeners(app_=app_)
    return app_


app = create_app()
