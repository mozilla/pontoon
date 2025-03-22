import sys
import copy
import socket
import logging
import jsonpickle
import requests
from raygun4py import raygunmsgs
from raygun4py import utilities

DEFAULT_CONFIG = {
    'before_send_callback': None,
    'grouping_key_callback': None,
    'filtered_keys': [],
    'ignored_exceptions': [],
    'proxy': None,
    'transmit_global_variables': True,
    'transmit_local_variables': True,
    'transmit_environment_variables': True,
    'userversion': "Not defined",
    'user': None,
    'http_timeout': 10.0
}

class RaygunSender:

    log = logging.getLogger(__name__)

    api_key = None
    endpointprotocol = 'https://'
    endpointhost = 'api.raygun.io'
    endpointpath = '/entries'

    def __init__(self, api_key, config={}):
        if (api_key):
            self.api_key = api_key
        else:
            self.log.warning("RaygunProvider error: ApiKey not set, errors will not be transmitted")

        try:
            import ssl
        except ImportError:
            self.log.warning("RaygunProvider error: No SSL support available, cannot send. Please"
                        "compile the socket module with SSL support.")

        # Set up the default values
        default_config = utilities.snakecase_dict(copy.deepcopy(DEFAULT_CONFIG))
        default_config.update(utilities.snakecase_dict(config or {}))
        for k, v in default_config.items():
            setattr(self, k, v)

    def set_version(self, version):
        if isinstance(version, str):
            self.userversion = version

    def set_user(self, user):
        self.user = user

    def ignore_exceptions(self, exceptions):
        if isinstance(exceptions, list):
            self.ignored_exceptions = exceptions

    def filter_keys(self, keys):
        if isinstance(keys, list):
            self.filtered_keys = keys

    def set_proxy(self, host, port):
        self.proxy = {
            'host': host,
            'port': port
        }

    def on_before_send(self, callback):
        if callable(callback):
            self.before_send_callback = callback

    def on_grouping_key(self, callback):
        if callable(callback):
            self.grouping_key_callback = callback

    def send_exception(self, exception=None, exc_info=None, **kwargs):
        options = {
            'transmitLocalVariables': self.transmit_local_variables,
            'transmitGlobalVariables': self.transmit_global_variables
        }

        if exc_info is None:
            exc_info = sys.exc_info()

        exc_type, exc_value, exc_traceback = exc_info

        if exception is not None:
            errorMessage = raygunmsgs.RaygunErrorMessage(type(exception), exception, exception.__traceback__, options)
        else:
            errorMessage = raygunmsgs.RaygunErrorMessage(exc_type, exc_value, exc_traceback, options)

        tags, custom_data, http_request, extra_environment_data = self._parse_args(kwargs)
        message = self._create_message(errorMessage, tags, custom_data, http_request, extra_environment_data)
        message = self._transform_message(message)

        if message is not None:
            return self._post(message)

    def _parse_args(self, kwargs):
        tags = kwargs['tags'] if 'tags' in kwargs else None
        custom_data = kwargs['userCustomData'] if 'userCustomData' in kwargs else None
        extra_environment_data = kwargs['extra_environment_data'] if 'extra_environment_data' in kwargs else None

        http_request = None
        if 'httpRequest' in kwargs:
            http_request = kwargs['httpRequest']
        elif 'request' in kwargs:
            http_request = kwargs['request']

        return tags, custom_data, http_request, extra_environment_data

    def _create_message(self, raygunExceptionMessage, tags, user_custom_data, http_request, extra_environment_data):
        options = {
            'transmit_environment_variables': self.transmit_environment_variables
        }

        return raygunmsgs.RaygunMessageBuilder(options).new() \
            .set_machine_name(socket.gethostname()) \
            .set_version(self.userversion) \
            .set_client_details() \
            .set_exception_details(raygunExceptionMessage) \
            .set_environment_details(extra_environment_data) \
            .set_tags(tags) \
            .set_customdata(user_custom_data) \
            .set_request_details(http_request) \
            .set_user(self.user) \
            .build()

    def _transform_message(self, message):
        message = utilities.ignore_exceptions(self.ignored_exceptions, message)

        if message is not None:
            message = utilities.filter_keys(self.filtered_keys, message)
            message['details']['groupingKey'] = utilities.execute_grouping_key(self.grouping_key_callback, message)

        if self.before_send_callback is not None:
            mutated_payload = self.before_send_callback(message['details'])

            if mutated_payload is not None:
                message['details'] = mutated_payload
            else:
                return None

        return message

    def _post(self, raygunMessage):
        json = jsonpickle.encode(raygunMessage, unpicklable=False)

        try:
            headers = {
                "X-ApiKey": self.api_key,
                "Content-Type": "application/json",
                "User-Agent": "raygun4py"
            }

            response = requests.post(self.endpointprotocol + self.endpointhost + self.endpointpath,
                                     headers=headers, data=json, timeout=self.http_timeout)
        except Exception as e:
            self.log.error(e)
            return 400, "Exception: Could not send"
        return response.status_code, response.text


class RaygunHandler(logging.Handler):
    def __init__(self, api_key, version=None):
        logging.Handler.__init__(self)
        self.sender = RaygunSender(api_key)
        self.version = version

    def emit(self, record):
        userCustomData = {
            "Logger Message": record.msg
        }
        self.sender.send_exception(userCustomData=userCustomData)
