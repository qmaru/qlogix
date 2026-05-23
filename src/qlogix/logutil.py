import logging
from contextlib import contextmanager
from contextvars import ContextVar
from typing import Iterator
from uuid import uuid4

trace_id_var: ContextVar[str] = ContextVar("trace_id", default="-")


class TraceIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        record.trace_id = trace_id_var.get()
        return True


def configure_logging() -> None:
    root = logging.getLogger()

    if root.handlers:
        return

    logging.basicConfig(
        level=logging.INFO, format=("%(levelname)s %(name)s trace_id=%(trace_id)s %(message)s")
    )

    for handler in root.handlers:
        handler.addFilter(TraceIdFilter())


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def set_trace_id(trace_id: str | None = None) -> str:
    value = trace_id or uuid4().hex[:12]
    trace_id_var.set(value)
    return value


@contextmanager
def log_stage(logger: logging.Logger, name: str) -> Iterator[None]:
    try:
        yield

    except Exception:
        logger.exception(f"{name}_failed")
        raise

    logger.info(f"{name} [DONE]")


def log_external_call(logger: logging.Logger, name: str, callback):
    with log_stage(logger, name):
        return callback()
