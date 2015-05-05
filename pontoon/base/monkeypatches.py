from django.contrib import admin as django_admin
from django.contrib.admin.sites import AdminSite

from session_csrf import anonymous_csrf


__all__ = ['patch']


# Idempotence! http://en.wikipedia.org/wiki/Idempotence
_has_patched = False


def patch():
    global _has_patched
    if _has_patched:
        return

    # Monkey-patch Django's csrf_protect decorator to use session-based CSRF
    # tokens:
    import session_csrf
    session_csrf.monkeypatch()
    django_admin.site = SessionCsrfAdminSite()

    # prevent it from being run again later
    _has_patched = True


class SessionCsrfAdminSite(AdminSite):
    """Custom admin site that handles login with session_csrf."""

    def login(self, request, extra_context=None):
        @anonymous_csrf
        def call_parent_login(request, extra_context):
            return super(SessionCsrfAdminSite, self).login(request,
                                                           extra_context)

        return call_parent_login(request, extra_context)
