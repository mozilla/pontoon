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
from collections import namedtuple

from newrelic.core.attribute_filter import (
    DST_ALL,
    DST_ERROR_COLLECTOR,
    DST_LOG_EVENT_CONTEXT_DATA,
    DST_SPAN_EVENTS,
    DST_TRANSACTION_EVENTS,
    DST_TRANSACTION_SEGMENTS,
    DST_TRANSACTION_TRACER,
)
from newrelic.packages import six

_logger = logging.getLogger(__name__)

_Attribute = namedtuple("_Attribute", ["name", "value", "destinations"])

# The following destinations are created here, never changed, and only
# used in create_agent_attributes. It is placed at the module level here
# as an optimization.

# All agent attributes go to transaction traces and error traces by default.

_DESTINATIONS = DST_ERROR_COLLECTOR | DST_TRANSACTION_TRACER | DST_TRANSACTION_SEGMENTS
_DESTINATIONS_WITH_EVENTS = _DESTINATIONS | DST_TRANSACTION_EVENTS | DST_SPAN_EVENTS

# The following subset goes to transaction events by default.

_TRANSACTION_EVENT_DEFAULT_ATTRIBUTES = set(
    (
        "aws.lambda.arn",
        "aws.lambda.coldStart",
        "aws.lambda.eventSource.arn",
        "aws.operation",
        "aws.requestId",
        "code.filepath",
        "code.function",
        "code.lineno",
        "code.namespace",
        "db.collection",
        "db.instance",
        "db.operation",
        "db.statement",
        "enduser.id",
        "error.class",
        "error.expected",
        "error.message",
        "error.group.name",
        "graphql.field.name",
        "graphql.field.parentType",
        "graphql.field.path",
        "graphql.field.returnType",
        "graphql.operation.name",
        "graphql.operation.query",
        "graphql.operation.type",
        "host.displayName",
        "http.statusCode",
        "http.url",
        "message.queueName",
        "message.routingKey",
        "peer.address",
        "peer.hostname",
        "request.headers.accept",
        "request.headers.contentLength",
        "request.headers.contentType",
        "request.headers.host",
        "request.headers.userAgent",
        "request.method",
        "request.uri",
        "response.headers.contentLength",
        "response.headers.contentType",
        "response.status",
    )
)

MAX_NUM_USER_ATTRIBUTES = 128
MAX_ATTRIBUTE_LENGTH = 255
MAX_64_BIT_INT = 2**63 - 1
MAX_LOG_MESSAGE_LENGTH = 32768


class NameTooLongException(Exception):
    pass


class NameIsNotStringException(Exception):
    pass


class IntTooLargeException(Exception):
    pass


class CastingFailureException(Exception):
    pass


class Attribute(_Attribute):
    def __repr__(self):
        return "Attribute(name=%r, value=%r, destinations=%r)" % (self.name, self.value, bin(self.destinations))


def create_attributes(attr_dict, destinations, attribute_filter):
    attributes = []

    for k, v in attr_dict.items():
        dest = attribute_filter.apply(k, destinations)
        attributes.append(Attribute(k, v, dest))

    return attributes


def create_agent_attributes(attr_dict, attribute_filter):
    attributes = []

    for k, v in attr_dict.items():
        if v is None:
            continue

        if k in _TRANSACTION_EVENT_DEFAULT_ATTRIBUTES:
            dest = attribute_filter.apply(k, _DESTINATIONS_WITH_EVENTS)
        else:
            dest = attribute_filter.apply(k, _DESTINATIONS)

        attributes.append(Attribute(k, v, dest))

    return attributes


def resolve_user_attributes(attr_dict, attribute_filter, target_destination, attr_class=dict):
    u_attrs = attr_class()

    for attr_name, attr_value in attr_dict.items():
        if attr_value is None:
            continue

        dest = attribute_filter.apply(attr_name, DST_ALL)

        if dest & target_destination:
            u_attrs[attr_name] = attr_value

    return u_attrs


def resolve_agent_attributes(attr_dict, attribute_filter, target_destination, attr_class=dict):
    a_attrs = attr_class()

    for attr_name, attr_value in attr_dict.items():
        if attr_value is None:
            continue

        if attr_name in _TRANSACTION_EVENT_DEFAULT_ATTRIBUTES:
            dest = attribute_filter.apply(attr_name, _DESTINATIONS_WITH_EVENTS)
        else:
            dest = attribute_filter.apply(attr_name, _DESTINATIONS)

        if dest & target_destination:
            a_attrs[attr_name] = attr_value

    return a_attrs


def resolve_logging_context_attributes(attr_dict, attribute_filter, attr_prefix, attr_class=dict):
    """
    Helper function for processing logging context attributes that require a prefix. Correctly filters attribute names
    before applying the required prefix, and then applies the process_user_attribute after the prefix is applied to
    correctly check length requirements.
    """
    c_attrs = attr_class()

    for attr_name, attr_value in attr_dict.items():
        dest = attribute_filter.apply(attr_name, DST_LOG_EVENT_CONTEXT_DATA)

        if dest & DST_LOG_EVENT_CONTEXT_DATA:
            try:
                attr_name, attr_value = process_user_attribute(attr_prefix + attr_name, attr_value)
                if attr_name:
                    c_attrs[attr_name] = attr_value
            except Exception:
                _logger.debug(
                    "Log event context attribute failed to validate for unknown reason. Dropping context attribute: %s. Check traceback for clues.",
                    attr_name,
                    exc_info=True,
                )

    return c_attrs


def create_user_attributes(attr_dict, attribute_filter):
    destinations = DST_ALL
    return create_attributes(attr_dict, destinations, attribute_filter)


def truncate(text, maxsize=MAX_ATTRIBUTE_LENGTH, encoding="utf-8", ending=None):
    # Truncate text so that its byte representation
    # is no longer than maxsize bytes.

    # If text is unicode (Python 2 or 3), return unicode.
    # If text is a Python 2 string, return str.

    if isinstance(text, six.text_type):
        truncated = _truncate_unicode(text, maxsize, encoding)
    else:
        truncated = _truncate_bytes(text, maxsize)
        ending = ending and ending.encode(encoding)

    if ending and truncated != text:
        truncated = truncated[: -len(ending)] + ending

    return truncated


def _truncate_unicode(u, maxsize, encoding="utf-8"):
    encoded = u.encode(encoding)[:maxsize]
    return encoded.decode(encoding, "ignore")


def _truncate_bytes(s, maxsize):
    return s[:maxsize]


def check_name_length(name, max_length=MAX_ATTRIBUTE_LENGTH, encoding="utf-8"):
    trunc_name = truncate(name, max_length, encoding)
    if name != trunc_name:
        raise NameTooLongException()


def check_name_is_string(name):
    if not isinstance(name, (six.text_type, six.binary_type)):
        raise NameIsNotStringException()


def check_max_int(value, max_int=MAX_64_BIT_INT):
    if isinstance(value, six.integer_types) and value > max_int:
        raise IntTooLargeException()


def process_user_attribute(name, value, max_length=MAX_ATTRIBUTE_LENGTH, ending=None):
    # Perform all necessary checks on a potential attribute.
    #
    # Returns:
    #       (name, value) if attribute is OK.
    #       (NONE, NONE) if attribute isn't.
    #
    # If any of these checks fail, they will raise an exception, so we
    # log a message, and return (None, None).

    FAILED_RESULT = (None, None)

    try:
        check_name_is_string(name)
        check_name_length(name)
        check_max_int(value)

        value = sanitize(value)

    except NameIsNotStringException:
        _logger.debug("Attribute name must be a string. Dropping attribute: %r=%r", name, value)
        return FAILED_RESULT

    except NameTooLongException:
        _logger.debug("Attribute name exceeds maximum length. Dropping attribute: %r=%r", name, value)
        return FAILED_RESULT

    except IntTooLargeException:
        _logger.debug("Attribute value exceeds maximum integer value. Dropping attribute: %r=%r", name, value)
        return FAILED_RESULT

    except CastingFailureException:
        _logger.debug("Attribute value cannot be cast to a string. Dropping attribute: %r=%r", name, value)
        return FAILED_RESULT

    else:
        # Check length after casting

        valid_types_text = (six.text_type, six.binary_type)

        if isinstance(value, valid_types_text):
            trunc_value = truncate(value, maxsize=max_length, ending=ending)
            if value != trunc_value:
                _logger.debug(
                    "Attribute value exceeds maximum length (%r bytes). Truncating value: %r=%r.",
                    max_length,
                    name,
                    trunc_value,
                )

            value = trunc_value

        return (name, value)


def sanitize(value):
    """
    Return value unchanged, if it's a valid type that is supported by
    Insights. Otherwise, convert value to a string.

    Raise CastingFailureException, if str(value) somehow fails.
    """

    valid_value_types = (six.text_type, six.binary_type, bool, float, six.integer_types)

    # When working with numpy, note that numpy has its own `int`s, `str`s,
    # et cetera. `numpy.str_` and `numpy.float_` inherit from Python's native
    # `str` and `float`, respectively.  However, some types, such as `numpy.int_`
    # and `numpy.bool_`, do not inherit from `int` and `bool` (respectively).
    # In those cases, the valid_value_types check fails and it will try to
    # convert these to string, which is not the desired behavior.  Checking for
    # `type` in lieu of `isinstance` has the potential to impact performance.

    # numpy values have an attribute "item" that returns the closest
    # equivalent Python native type.  Ex: numpy.int64 -> int
    # This is important to utilize in cases like int and bool where
    # numpy does not inherit from those classes. This logic is
    # determining whether or not the value is a valid_value_type (or
    # inherited from one of those types) AND whether it is a numpy
    # type (by determining if it has the attribute "item").
    if not isinstance(value, valid_value_types) and not hasattr(value, "item"):
        original = value

        try:
            value = str(value)
        except Exception:
            raise CastingFailureException()
        else:
            _logger.debug("Attribute value is of type: %r. Casting %r to string: %s", type(original), original, value)

    return value
