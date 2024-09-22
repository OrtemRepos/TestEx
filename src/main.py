from collections.abc import Callable

import structlog
import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from src.auth.router import auth_router
from src.logging_config import logger


async def lifespan(app: FastAPI):
    await logger.ainfo("app started")
    yield
    await logger.ainfo("app stopped")


app = FastAPI(lifespan=lifespan)

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.exception("Request validation error")
    logger.exception("Request validation error", exc_info=exc)

@app.exception_handler(Exception)
async def exception_handler(request: Request, exc: Exception):
    logger.exception("Internal server error", exc_info=exc)

@app.middleware("http")
async def logging_middleware(request: Request, call_next: Callable):
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        method=request.method,
        path=request.url.path,
        host=request.client.host,  # type: ignore
        port=request.client.port,  # type: ignore
    )

    response = await call_next(request)
    
    structlog.contextvars.bind_contextvars(
        status_code=response.status_code,
    )
    return response


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, tags=["auth"])


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
