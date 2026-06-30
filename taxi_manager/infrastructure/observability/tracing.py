from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, TypeVar, ParamSpec

from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode


tracer = trace.get_tracer("taxi-manager.api")

P = ParamSpec("P")
R = TypeVar("R")


@contextmanager
def trace_span(
    name: str,
    *,
    stage: str | None = None,
    attrs: dict[str, Any] | None = None,
):
    """
    Универсальный span для Tempo.

    Использование:
        with trace_span("api.serialize"):
            ...

    Не дублируем route/method — они уже есть на корневом HTTP-span.
    """

    with tracer.start_as_current_span(name) as span:
        if stage:
            span.set_attribute("app.stage", stage)

        if attrs:
            for key, value in attrs.items():
                if value is not None:
                    span.set_attribute(key, value)

        try:
            yield span
        except Exception as exc:
            span.record_exception(exc)
            span.set_status(Status(StatusCode.ERROR, str(exc)))
            raise

def trace_method(
    name: str | None = None,
    *,
    stage: str | None = None,
    attrs: dict[str, Any] | None = None,
):
    """
    Декоратор для грубой разметки методов.

    Использование:
        @trace_method("api.business_logic")
        def method(...):
            ...
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        span_name = name or f"{func.__module__}.{func.__qualname__}"

        @wraps(func)
        def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            with trace_span(
                span_name,
                stage=stage,
                attrs={
                    "code.function": func.__qualname__,
                    "code.namespace": func.__module__,
                    **(attrs or {}),
                },
            ):
                return func(*args, **kwargs)

        return wrapper

    return decorator