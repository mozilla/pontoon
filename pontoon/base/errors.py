import logging

from django.conf import settings

from raygun4py import raygunprovider


log = logging.getLogger(__name__)


def send_exception(exception, exc_info=None):
    """
    Function sends exception to selected provider.
    """
    api_key = settings.RAYGUN4PY_CONFIG["api_key"]
    if api_key:
        provider = raygunprovider.RaygunSender(api_key)
        provider.send_exception(exception, exc_info=exc_info)
    else:
        log.error(exception, exc_info=exc_info)
