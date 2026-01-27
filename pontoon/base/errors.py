import logging


log = logging.getLogger(__name__)


def send_exception(exception, exc_info=None):
    """
    Function sends exception to selected provider.
    """
    log.error(exception, exc_info=exc_info)
