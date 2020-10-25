from django.apps import AppConfig


class BaseConfig(AppConfig):
    name = "pontoon.base"
    verbose_name = "Base"

    def ready(self):
        super(BaseConfig, self).ready()

        # Load celery app so celery.shared_task uses it for executing
        # tasks.
        from pontoon.base.celeryapp import app as celery_app  # NOQA

        # Load and register signals.
        from pontoon.base import signals  # NOQA
