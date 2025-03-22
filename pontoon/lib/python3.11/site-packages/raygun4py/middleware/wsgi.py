import logging

from raygun4py import raygunprovider, http_utilities


log = logging.getLogger(__name__)


class Provider(object):

    def __init__(self, app, apiKey):
        self.app = app
        self.sender = raygunprovider.RaygunSender(apiKey)

    def __call__(self, environ, start_response):
        if not self.sender:
            log.error("Raygun-WSGI: Cannot send as provider not attached")

        iterable = None

        try:
            iterable = self.app(environ, start_response)
            for event in iterable:
                yield event

        except Exception as e:
            try:
                request = http_utilities.build_wsgi_compliant_request(environ)
                self.sender.send_exception(exception=e, request=request)
            except Exception as inner:
                log.error("Raygun-WSGI: could not send exception!")
                log.error(inner)

            raise

        finally:
            if hasattr(iterable, 'close'):
                try:
                    iterable.close()
                except Exception as e:
                    try:
                        rg_request_details = http_utilities.build_wsgi_compliant_request(environ)
                        self.sender.send_exception(exception=e, request=rg_request_details)
                    except Exception as inner:
                        log.error("Raygun-WSGI: could not send exception on close!")
                        log.error(inner)
                    raise

