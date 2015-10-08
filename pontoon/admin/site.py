from django_browserid.admin import BrowserIDAdminSite
from session_csrf import anonymous_csrf


class PontoonAdminSite(BrowserIDAdminSite):
    site_header = 'Pontoon Administration'
    site_title = 'Pontoon Admin'
    index_title = 'Pontoon Administration'

    def login(self, request, extra_context=None):
        """Enable anonymous CSRF on the admin login page."""
        @anonymous_csrf
        def call_parent_login(request, extra_context):
            return super(PontoonAdminSite, self).login(request, extra_context)

        return call_parent_login(request, extra_context)


admin_site = PontoonAdminSite(name='pontoon')
