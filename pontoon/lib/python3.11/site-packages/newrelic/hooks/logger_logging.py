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

from newrelic.api.application import application_instance
from newrelic.api.time_trace import get_linking_metadata
from newrelic.api.transaction import current_transaction, record_log_event
from newrelic.common.object_wrapper import function_wrapper, wrap_function_wrapper
from newrelic.core.config import global_settings

try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote


IGNORED_LOG_RECORD_KEYS = set(["message", "msg"])


def add_nr_linking_metadata(message):
    available_metadata = get_linking_metadata()
    entity_name = quote(available_metadata.get("entity.name", ""))
    entity_guid = available_metadata.get("entity.guid", "")
    span_id = available_metadata.get("span.id", "")
    trace_id = available_metadata.get("trace.id", "")
    hostname = available_metadata.get("hostname", "")

    nr_linking_str = "|".join(("NR-LINKING", entity_guid, hostname, trace_id, span_id, entity_name))
    return "%s %s|" % (message, nr_linking_str)


@function_wrapper
def wrap_getMessage(wrapped, instance, args, kwargs):
    message = wrapped(*args, **kwargs)
    return add_nr_linking_metadata(message)


def bind_callHandlers(record):
    return record


def wrap_callHandlers(wrapped, instance, args, kwargs):
    transaction = current_transaction()
    record = bind_callHandlers(*args, **kwargs)

    logger_name = getattr(instance, "name", None)
    if logger_name and logger_name.split(".")[0] == "newrelic":
        return wrapped(*args, **kwargs)

    if transaction:
        settings = transaction.settings
    else:
        settings = global_settings()

    # Return early if application logging not enabled
    if settings and settings.application_logging and settings.application_logging.enabled:
        level_name = str(getattr(record, "levelname", "UNKNOWN"))
        if settings.application_logging.metrics and settings.application_logging.metrics.enabled:
            if transaction:
                transaction.record_custom_metric("Logging/lines", {"count": 1})
                transaction.record_custom_metric("Logging/lines/%s" % level_name, {"count": 1})
            else:
                application = application_instance(activate=False)
                if application and application.enabled:
                    application.record_custom_metric("Logging/lines", {"count": 1})
                    application.record_custom_metric("Logging/lines/%s" % level_name, {"count": 1})

        if settings.application_logging.forwarding and settings.application_logging.forwarding.enabled:
            try:
                message = record.msg
                if not isinstance(message, dict):
                    # Allow python to convert the message to a string and template it with args.
                    message = record.getMessage()

                # Grab and filter context attributes from log record
                record_attrs = vars(record)
                context_attrs = {k: record_attrs[k] for k in record_attrs if k not in IGNORED_LOG_RECORD_KEYS}

                record_log_event(
                    message=message, level=level_name, timestamp=int(record.created * 1000), attributes=context_attrs
                )
            except Exception:
                pass

        if settings.application_logging.local_decorating and settings.application_logging.local_decorating.enabled:
            record._nr_original_message = record.getMessage
            record.getMessage = wrap_getMessage(record.getMessage)

    return wrapped(*args, **kwargs)


def instrument_logging(module):
    if hasattr(module, "Logger"):
        if hasattr(module.Logger, "callHandlers"):
            wrap_function_wrapper(module, "Logger.callHandlers", wrap_callHandlers)
