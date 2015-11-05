from raygun4py import raygunprovider

from django.conf import settings

def send_exception(exc):
    """
    Function sends exception to selected provider.
    """
    raygunprovider.RaygunSender(settings.RAYGUN4PY_API_KEY).send_exception(exc)
