from django.apps import AppConfig


class ObservabilityConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "taxi_manager.infrastructure.observability"

    def ready(self):
        from .profiling import setup_pyroscope

        setup_pyroscope()