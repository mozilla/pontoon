import logging
import flask
from flask.signals import got_request_exception
from raygun4py import raygunprovider

log = logging.getLogger(__name__)


class Provider(object):
    def __init__(self, flaskApp, apiKey):
        self.flaskApp = flaskApp
        self.apiKey = apiKey
        self.sender = None

        got_request_exception.connect(self.send_exception, sender=flaskApp)

        flaskApp.extensions['raygun'] = self

    def attach(self):
        if not hasattr(self.flaskApp, 'extensions'):
            self.flaskApp.extensions = {}

        self.sender = raygunprovider.RaygunSender(self.apiKey)
        return self.sender

    def send_exception(self, *args, **kwargs):
        if not self.sender:
            log.error("Raygun-Flask: Cannot send as provider not attached")

        env = self._get_flask_environment()
        self.sender.send_exception(extra_environment_data=env)

    def _get_flask_environment(self):
        return {
            'frameworkVersion': 'Flask ' + getattr(flask, '__version__', '')
        }
