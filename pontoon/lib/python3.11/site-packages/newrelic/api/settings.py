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

import logging

import newrelic.core.config

settings = newrelic.core.config.global_settings

_logger = logging.getLogger(__name__)


RECORDSQL_OFF = 'off'
RECORDSQL_RAW = 'raw'
RECORDSQL_OBFUSCATED = 'obfuscated'

COMPRESSED_CONTENT_ENCODING_DEFLATE = 'deflate'
COMPRESSED_CONTENT_ENCODING_GZIP = 'gzip'

STRIP_EXCEPTION_MESSAGE = ("Message removed by New Relic 'strip_exception_messages' setting")


def set_error_group_callback(callback, application=None):
    """Set the current callback to be used to determine error groups."""
    from newrelic.api.application import application_instance

    if callback is not None and not callable(callback):
        _logger.error("Error group callback must be a callable, or None to unset this setting.")
        return

    # Check for activated application if it exists and was not given.
    application = application_instance(activate=False) if application is None else application

    # Get application settings if it exists, or fallback to global settings object
    _settings = application.settings if application is not None else settings()

    if _settings is None:
        _logger.error("Failed to set error_group_callback in application settings. Report this issue to New Relic support.")
        return

    if _settings.error_collector:
        _settings.error_collector._error_group_callback = callback
