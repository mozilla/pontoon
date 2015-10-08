from django.apps import AppConfig

import session_csrf


class BaseConfig(AppConfig):
    name = 'pontoon.base'
    verbose_name = 'Base'

    _has_patched = False

    def ready(self):
        super(BaseConfig, self).ready()
        self.monkeypatch()

        # Load celery app so celery.shared_task uses it for executing
        # tasks.
        from pontoon.base.celery import app as celery_app  # NOQA

        # Load and register signals.
        from pontoon.base import signals  # NOQA

    def monkeypatch(self):
        # Only patch once, ever.
        if BaseConfig._has_patched:
            return

        # Monkey-patch Django's csrf_protect decorator to use
        # session-based CSRF tokens:
        session_csrf.monkeypatch()

        BaseConfig._has_patched = True
