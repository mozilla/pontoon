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

from newrelic.api.asgi_application import ASGIApplicationWrapper
from newrelic.common.package_version_utils import get_package_version


@property
def application(self):
    return getattr(self, "_nr_application", vars(self).get("application", None))


@application.setter
def application(self, value):
    dispatcher_details = ("Daphne", get_package_version("daphne"))
    # Wrap app only once
    if value and not getattr(value, "_nr_wrapped", False):
        value = ASGIApplicationWrapper(value, dispatcher=dispatcher_details)
        value._nr_wrapped = True
    self._nr_application = value


def instrument_daphne_server(module):
    module.Server.application = application
