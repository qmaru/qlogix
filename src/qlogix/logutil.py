import logging
from contextlib import contextmanager
from contextvars import ContextVar
from threading import Lock
from time import perf_counter
from typing import Iterator
from uuid import uuid4

trace_id_var: ContextVar[str] = ContextVar("trace_id", default="-")
_global_trace_id = "-"
_global_trace_id_lock = Lock()


class TraceIdFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        trace_id = trace_id_var.get()
        if trace_id == "-":
            with _global_trace_id_lock:
                trace_id = _global_trace_id
        record.trace_id = trace_id
        return True


def configure_logging() -> None:
    root = logging.getLogger()
    if root.handlers:
        return

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s trace_id=%(trace_id)s %(message)s",
    )
    for handler in root.handlers:
        handler.addFilter(TraceIdFilter())


def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)


def set_trace_id(trace_id: str | None = None) -> str:
    global _global_trace_id

    value = trace_id or uuid4().hex[:12]
    trace_id_var.set(value)
    with _global_trace_id_lock:
        _global_trace_id = value
    return value


def _format_fields(**fields: object) -> str:
    items = [f"{key}={value}" for key, value in fields.items() if value is not None]
    if not items:
        return ""
    return " " + " ".join(items)


@contextmanager
def log_stage(logger: logging.Logger, stage: str, **fields: object) -> Iterator[None]:
    logger.info("stage_start stage=%s%s", stage, _format_fields(**fields))
    started_at = perf_counter()
    try:
        yield
    finally:
        elapsed_ms = (perf_counter() - started_at) * 1000
        logger.info(
            "stage_end stage=%s elapsed_ms=%.2f%s",
            stage,
            elapsed_ms,
            _format_fields(**fields),
        )


def log_external_call(logger: logging.Logger, operation: str, callback, **fields: object):
    started_at = perf_counter()
    try:
        return callback()
    finally:
        elapsed_ms = (perf_counter() - started_at) * 1000
        logger.info(
            "external_call operation=%s elapsed_ms=%.2f%s",
            operation,
            elapsed_ms,
            _format_fields(**fields),
        )
