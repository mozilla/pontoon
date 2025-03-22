from django.conf import settings as django_settings
from django.core.exceptions import ImproperlyConfigured
from django.views.static import serve

from .collector import default_collector
from .conf import settings


def serve_static(request, path, insecure=False, **kwargs):
    """Collect and serve static files.

    This view serves up static files, much like Django's
    :py:func:`~django.views.static.serve` view, with the addition that it
    collects static files first (if enabled). This allows images, fonts, and
    other assets to be served up without first loading a page using the
    ``{% javascript %}`` or ``{% stylesheet %}`` template tags.

    You can use this view by adding the following to any :file:`urls.py`::

        urlpatterns += static('static/', view='pipeline.views.serve_static')
    """
    # Follow the same logic Django uses for determining access to the
    # static-serving view.
    if not django_settings.DEBUG and not insecure:
        raise ImproperlyConfigured(
            "The staticfiles view can only be used in "
            "debug mode or if the --insecure "
            "option of 'runserver' is used"
        )

    if not settings.PIPELINE_ENABLED and settings.PIPELINE_COLLECTOR_ENABLED:
        # Collect only the requested file, in order to serve the result as
        # fast as possible. This won't interfere with the template tags in any
        # way, as those will still cause Django to collect all media.
        default_collector.collect(request, files=[path])

    return serve(request, path, document_root=django_settings.STATIC_ROOT, **kwargs)
