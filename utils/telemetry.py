import logging
import os
from dotenv import load_dotenv

load_dotenv()

# Set this BEFORE any other imports to enable AI Agent Service tracing
os.environ.setdefault("AZURE_TRACING_GEN_AI_CONTENT_RECORDING_ENABLED", "true")

from azure.monitor.opentelemetry import configure_azure_monitor
from opentelemetry._logs import set_logger_provider
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.semconv.resource import ResourceAttributes
from opentelemetry.sdk.resources import Resource
from azure.monitor.opentelemetry.exporter import AzureMonitorLogExporter

connection_string = os.getenv("APPLICATION_INSIGHTS_CONNECTION_STRING")
service_name = os.getenv("SERVICE_NAME", "appmodagents")
resource = Resource.create({ResourceAttributes.SERVICE_NAME: service_name})

_initialized = False


def set_up_logging():
    """Set up custom logging handler for semantic_kernel logs only."""
    if not connection_string:
        return
    
    exporter = AzureMonitorLogExporter(connection_string=connection_string)
    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(exporter))
    set_logger_provider(logger_provider)

    # Create a logging handler specifically for semantic_kernel
    handler = LoggingHandler()
    handler.addFilter(logging.Filter("semantic_kernel"))
    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)


def init():
    """Initialize telemetry using Azure Monitor configure_azure_monitor for AI Agent Service support.
    
    This approach ensures AI Agent Service traces appear in Azure AI Foundry portal.
    """
    global _initialized
    if _initialized:
        return
    if not connection_string:
        logging.getLogger(__name__).debug(
            "Telemetry disabled: APPLICATION_INSIGHTS_CONNECTION_STRING not set"
        )
        _initialized = True
        return
    try:
        # Use configure_azure_monitor instead of manual setup for better AI Agent Service integration
        configure_azure_monitor(
            connection_string=connection_string,
            resource=resource
        )
        
        # Add custom logging for semantic_kernel
        set_up_logging()
        
        _initialized = True
        logging.getLogger(__name__).info("Telemetry initialized for service '%s'", service_name)
        print(f'Telemetry initialized with AI Agent Service tracing enabled (service: {service_name})')
    except Exception as e:
        logging.getLogger(__name__).warning("Telemetry initialization failed: %s", e)
        _initialized = True

# Auto-init on import
init()

__all__ = [
    "init",
]