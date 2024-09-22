import logging
import os

import structlog

level = os.environ.get("LOG_LEVEL")
assert level

LOG_LEVEL = getattr(logging, level)


def get_renderer():
    if os.environ.get("PROD"):
        return structlog.processors.JSONRenderer()
    return structlog.dev.ConsoleRenderer()


def get_logger_factory():
    if os.environ.get("PROD"):
        with open("logs/app.log", "w+t") as file:
            return structlog.WriteLoggerFactory(file=file)

    return structlog.PrintLoggerFactory()


structlog.configure(
    wrapper_class=structlog.make_filtering_bound_logger(LOG_LEVEL),
    processors=[
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        get_renderer(),
    ],
    logger_factory=get_logger_factory(),
)
logger = structlog.get_logger("main")
