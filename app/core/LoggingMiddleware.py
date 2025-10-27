from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from uuid import uuid4
import structlog

class LoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        request_id = str(uuid4())
        log = structlog.get_logger()
        logger = log.bind(
            request_id = request_id,
            method = request.method,
            path = request.url.path
        )
        request.state.logger = logger
        response = await call_next(request)
        logger.info(
            "Request processed",
            status_code=response.status_code,
        )
        logger.unbind("request_id")
        logger.unbind("method")
        logger.unbind("path")
        return response