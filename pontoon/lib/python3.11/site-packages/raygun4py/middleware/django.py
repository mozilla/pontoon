import django
from django.conf import settings
from raygun4py import raygunprovider
from django.utils.functional import cached_property

try:
    from django.utils.deprecation import MiddlewareMixin
except ImportError:
    MiddlewareMixin = object

class Provider(MiddlewareMixin):

    def __init__(self, get_response=None):
        self.get_response = get_response
        config = getattr(settings, 'RAYGUN4PY_CONFIG', {})
        apiKey = getattr(settings, 'RAYGUN4PY_API_KEY', config.get('api_key', None))

        self.sender = raygunprovider.RaygunSender(apiKey, config=config)

    def process_exception(self, request, exception):
        raygun_request = self._mapRequest(request)
        env = self._get_django_environment()

        self.sender.send_exception(exception=exception, request=raygun_request, extra_environment_data=env)

    def _mapRequest(self, request):
        headers = request.META.items()
        _headers = dict()
        for k, v in headers:
            if not k.startswith('wsgi'):
                _headers[k] = v

        return {
            'hostName': request.get_host(),
            'url': request.path,
            'httpMethod': request.method,
            'ipAddress': request.META.get('REMOTE_ADDR', '?'),
            'queryString': dict((key, request.GET[key]) for key in request.GET),
            'form': dict((key, request.POST[key]) for key in request.POST),
            'headers': _headers,
            'rawData': request.body if hasattr(request, 'body') else getattr(request, 'raw_post_data', {})
        }

    def _get_django_environment(self):
        return {
            'frameworkVersion': django.get_version()
        }
