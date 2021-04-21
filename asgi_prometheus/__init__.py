"""Support cookie-encrypted sessions for ASGI applications."""

import os
import time
from typing import Awaitable, Sequence, Set

from asgi_tools.middleware import BaseMiddeware
from asgi_tools.response import ResponseText
from asgi_tools.typing import ASGIApp, Scope, Receive, Send, Message
from prometheus_client import (
    REGISTRY, CollectorRegistry, Counter, Gauge, Histogram, generate_latest
)
from prometheus_client.multiprocess import MultiProcessCollector


__version__ = "1.0.0"
__license__ = "MIT"


REQUESTS = Counter(
    "requests_count",
    "Count of requests by method and path.",
    ["method", "path"]
)

REQUESTS_TIME = Histogram(
    "requests_time",
    "Histogram of requests processing time by path (in seconds)",
    ["method", "path"]
)

REQUESTS_IN_PROGRESS = Gauge(
    "requests_in_progress",
    "Gauge of requests by method and path currently being processed",
    ["method", "path"]
)

RESPONSES = Counter(
    "responses_count",
    "Count of responses by method, path and status codes.",
    ["method", "path", "status"]
)

EXCEPTIONS = Counter(
    "exceptions_count",
    "Count of exceptions raised by path and exception type",
    ["method", "path", "exception"],
)


class PrometheusMiddleware(BaseMiddeware):
    """Support prometheus metrics."""

    def __init__(
            self, app: ASGIApp, group_paths: Sequence = None, metrics_url: str = '/prometheus'):
        """Init the middleware."""
        super(PrometheusMiddleware, self).__init__(app)
        self.metrics_url = metrics_url
        self.group_paths = set(group_paths or [])

    async def __process__(self, scope: Scope, receive: Receive, send: Send):
        """Record metrics."""
        path, method = scope['path'], scope['method']
        if path == self.metrics_url:
            return await ResponseText(get_metrics())(scope, receive, send)

        path = process_path(path, self.group_paths)

        REQUESTS.labels(method=method, path=path).inc()
        REQUESTS_IN_PROGRESS.labels(method=method, path=path).inc()

        def custom_send(msg: Message) -> Awaitable:
            if msg['type'] == 'http.response.start':
                RESPONSES.labels(method=method, path=path, status=msg['status']).inc()

            return send(msg)

        try:
            before_time = time.perf_counter()
            res = await self.app(scope, receive, custom_send)
            after_time = time.perf_counter()
            REQUESTS_TIME.labels(method=method, path=path).observe(after_time - before_time)
            return res

        except Exception as exc:
            EXCEPTIONS.labels(method=method, path=path, exception=type(exc).__name__).inc()
            raise exc from None

        finally:
            REQUESTS_IN_PROGRESS.labels(method=method, path=path).dec()


def process_path(path: str, prefixes: Set) -> str:
    """Search the path by prefix in prefixes."""
    while path:
        if path in prefixes:
            return f"{path}*"
        path, *_ = path.rsplit('/', 1)

    return path


def get_metrics() -> str:
    """Get collected metrics."""
    registry = REGISTRY
    if 'PROMETHEUS_MULTIPROC_DIR' in os.environ:
        registry = CollectorRegistry()
        MultiProcessCollector(registry)

    return generate_latest(registry)
