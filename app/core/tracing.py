import logging
from functools import wraps

from flask import Flask
from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import DEPLOYMENT_ENVIRONMENT, Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from .config import TracingSettings

logger = logging.getLogger(__name__)


def setup(app: Flask):
    settings = TracingSettings()
    if not settings.enabled:
        logger.warning("Tracing disabled")
        return

    logger.warning("Tracing enabled for service: %s", settings.service_name)

    resource = Resource.create(
        {
            SERVICE_NAME: settings.service_name,
            DEPLOYMENT_ENVIRONMENT: settings.environment,
        }
    )
    provider = TracerProvider(resource=resource)
    trace.set_tracer_provider(provider)
    jaeger_exporter = JaegerExporter(
        agent_host_name=settings.agent_host_name,
        agent_port=settings.agent_port,
    )
    span_processor = BatchSpanProcessor(jaeger_exporter)
    provider.add_span_processor(span_processor)

    FlaskInstrumentor.instrument_app(app)


def tracer(name: str, tracer_name: str):
    """Decorate function to trace it with OpenTelemetry."""
    _tracer = trace.get_tracer(tracer_name)

    def real_decorator(func):
        if not TracingSettings().enabled:
            return func

        @wraps(func)
        def wrapper(*args, **kwargs):
            with _tracer.start_as_current_span(name):
                return func(*args, **kwargs)

        return wrapper

    return real_decorator
