import logging
import time

from opentelemetry import trace

logger = logging.getLogger(__name__)


def format_trace_id(trace_id: int) -> str:
    if trace_id == 0:
        return ""

    return format(trace_id, "032x")


def format_span_id(span_id: int) -> str:
    if span_id == 0:
        return ""

    return format(span_id, "016x")


class RequestTraceLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start = time.perf_counter()

        response = self.get_response(request)

        elapsed_ms = (time.perf_counter() - start) * 1000

        span = trace.get_current_span()
        span_context = span.get_span_context()

        trace_id = format_trace_id(span_context.trace_id)
        span_id = format_span_id(span_context.span_id)

        logger.info(
            "Request completed trace_id=%s span_id=%s method=%s path=%s status=%s elapsed=%.3f ms",
            trace_id,
            span_id,
            request.method,
            request.path,
            response.status_code,
            elapsed_ms,
        )

        return response