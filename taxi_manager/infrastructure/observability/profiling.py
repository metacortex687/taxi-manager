import logging
import os

logger = logging.getLogger(__name__)


def setup_pyroscope() -> None:
    enabled = os.getenv("PYROSCOPE_ENABLED", "false").lower() == "true"

    if not enabled:
        return

    try:
        import pyroscope
    except ImportError:
        logger.warning("Pyroscope is enabled, but pyroscope-io is not installed")
        return

    pyroscope.configure(
        application_name=os.getenv("PYROSCOPE_APPLICATION_NAME", "taxi-manager-django"),
        server_address=os.getenv("PYROSCOPE_SERVER_ADDRESS", "http://pyroscope:4040"),
        sample_rate=int(os.getenv("PYROSCOPE_SAMPLE_RATE", "100")),
        oncpu=True,
        gil_only=True,
        enable_logging=False,
        tags={
            "environment": os.getenv("DEPLOYMENT_ENVIRONMENT", "dev"),
            "service_name": os.getenv("OTEL_SERVICE_NAME", "taxi-manager-django"),
        },
    )

    logger.info("Pyroscope profiling enabled")