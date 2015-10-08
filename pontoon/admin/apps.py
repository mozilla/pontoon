from django.apps import AppConfig


class AdminConfig(AppConfig):
    name = 'pontoon.admin'
    label = 'pontoon_admin'
    verbose_name = 'Admin'

    def ready(self):
        super(AdminConfig, self).ready()

        # Import model_admins so they are registered on the site.
        import pontoon.admin.model_admins  # NOQA
