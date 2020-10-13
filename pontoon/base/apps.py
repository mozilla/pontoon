from django.apps import AppConfig
from django.contrib import admin
from django.contrib.admin.sites import AdminSite

import session_csrf
from session_csrf import anonymous_csrf


class BaseConfig(AppConfig):
    name = "pontoon.base"
    verbose_name = "Base"

    _has_patched = False

    def ready(self):
        super(BaseConfig, self).ready()
        self.monkeypatch()

        # Load celery app so celery.shared_task uses it for executing
        # tasks.
        from pontoon.base.celeryapp import app as celery_app  # NOQA

        # Load and register signals.
        from pontoon.base import signals  # NOQA

    def monkeypatch(self):
        # Only patch once, ever.
        if BaseConfig._has_patched:
            return

        # Monkey-patch Django's csrf_protect decorator to use
        # session-based CSRF tokens:
        session_csrf.monkeypatch()
        admin.site = SessionCsrfAdminSite()

        BaseConfig._has_patched = True


class SessionCsrfAdminSite(AdminSite):
    """Custom admin site that handles login with session_csrf."""

    def login(self, request, extra_context=None):
        @anonymous_csrf
        def call_parent_login(request, extra_context):
            return super(SessionCsrfAdminSite, self).login(request, extra_context)

        return call_parent_login(request, extra_context)
