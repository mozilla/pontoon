# Copyright 2010 New Relic, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from newrelic.api.in_function import wrap_in_function
from newrelic.api.wsgi_application import WSGIApplicationWrapper
from newrelic.common.package_version_utils import get_package_version


def instrument_waitress_server(module):
    def wrap_wsgi_application_entry_point(server, application, *args, **kwargs):
        dispatcher_details = ("Waitress", get_package_version("waitress"))
        application = WSGIApplicationWrapper(application, dispatcher=dispatcher_details)
        args = [server, application] + list(args)
        return (args, kwargs)

    wrap_in_function(module, "WSGIServer.__init__", wrap_wsgi_application_entry_point)
