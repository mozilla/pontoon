import logging

from django.conf import settings

from raygun4py import raygunprovider


log = logging.getLogger(__name__)


def send_exception(exception, exc_info=None):
    """
    Function sends exception to selected provider.
    """
    if settings.RAYGUN4PY_API_KEY:
        provider = raygunprovider.RaygunSender(settings.RAYGUN4PY_API_KEY)
        provider.send_exception(exception, exc_info=exc_info)
    else:
        log.error(exception, exc_info=exc_info)
