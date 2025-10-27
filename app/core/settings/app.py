import logging
import sys
from typing import Any, Dict, List, Tuple
import structlog
from pydantic import PostgresDsn, SecretStr

from app.core.settings.base import BaseAppSettings
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.sdk.resources import Resource

class AppSettings(BaseAppSettings):
    debug: bool = False
    docs_url: str = "/docs"
    openapi_prefix: str = ""
    openapi_url: str = "/openapi.json"
    redoc_url: str = "/redoc"
    title: str = "FastAPI example application"
    version: str = "0.0.0"

    database_url: PostgresDsn
    max_connection_count: int = 10
    min_connection_count: int = 10

    secret_key: SecretStr

    api_prefix: str = "/api"

    jwt_token_prefix: str = "Token"

    allowed_hosts: List[str] = ["*"]

    logging_level: int = logging.INFO
    loggers: Tuple[str, str] = ("uvicorn.asgi", "uvicorn.access")

    class Config:
        validate_assignment = True

    @property
    def fastapi_kwargs(self) -> Dict[str, Any]:
        return {
            "debug": self.debug,
            "docs_url": self.docs_url,
            "openapi_prefix": self.openapi_prefix,
            "openapi_url": self.openapi_url,
            "redoc_url": self.redoc_url,
            "title": self.title,
            "version": self.version,
        }

    def configure_logging(self) -> None:
        logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(message)s")
        structlog.configure(
            processors=[
                structlog.processors.TimeStamper(fmt="%Y-%m-%dT%H:%M:%S%z"),
                structlog.processors.JSONRenderer()
            ],
            context_class=dict,
            logger_factory=structlog.stdlib.LoggerFactory(),
            wrapper_class=structlog.stdlib.BoundLogger,
            cache_logger_on_first_use=True
        )
    def configure_tracing(self) -> None:
        # Set the global tracer provider
        resource = Resource(attributes={
        "service.name": "fastapi-realworld-app",  # Set the service name
        })
    
        trace.set_tracer_provider(
            TracerProvider(resource=resource)
        )

        # Set up Jaeger exporter for tracing
        jaeger_exporter = JaegerExporter(
            agent_host_name="localhost",  # Replace with your Jaeger agent host
            agent_port=6831,              # Default Jaeger agent port
        )

        # Add the BatchSpanProcessor to the tracer provider
        trace.get_tracer_provider().add_span_processor(BatchSpanProcessor(jaeger_exporter))

        # Automatically instrument FastAPI and SQLAlchemy
        FastAPIInstrumentor().instrument()
        SQLAlchemyInstrumentor().instrument()