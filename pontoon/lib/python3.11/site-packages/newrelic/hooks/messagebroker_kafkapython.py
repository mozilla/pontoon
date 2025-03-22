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
import sys

from kafka.serializer import Serializer

from newrelic.api.application import application_instance
from newrelic.api.function_trace import FunctionTraceWrapper
from newrelic.api.message_trace import MessageTrace
from newrelic.api.message_transaction import MessageTransaction
from newrelic.api.time_trace import current_trace, notice_error
from newrelic.api.transaction import current_transaction
from newrelic.common.object_wrapper import (
    ObjectProxy,
    function_wrapper,
    wrap_function_wrapper,
)
from newrelic.common.package_version_utils import get_package_version

HEARTBEAT_POLL = "MessageBroker/Kafka/Heartbeat/Poll"
HEARTBEAT_SENT = "MessageBroker/Kafka/Heartbeat/Sent"
HEARTBEAT_FAIL = "MessageBroker/Kafka/Heartbeat/Fail"
HEARTBEAT_RECEIVE = "MessageBroker/Kafka/Heartbeat/Receive"
HEARTBEAT_SESSION_TIMEOUT = "MessageBroker/Kafka/Heartbeat/SessionTimeout"
HEARTBEAT_POLL_TIMEOUT = "MessageBroker/Kafka/Heartbeat/PollTimeout"


def _bind_send(topic, value=None, key=None, headers=None, partition=None, timestamp_ms=None):
    return topic, value, key, headers, partition, timestamp_ms


def wrap_KafkaProducer_send(wrapped, instance, args, kwargs):
    transaction = current_transaction()

    if transaction is None:
        return wrapped(*args, **kwargs)

    topic, value, key, headers, partition, timestamp_ms = _bind_send(*args, **kwargs)
    headers = list(headers) if headers else []

    transaction.add_messagebroker_info("Kafka-Python", get_package_version("kafka-python"))

    with MessageTrace(
        library="Kafka",
        operation="Produce",
        destination_type="Topic",
        destination_name=topic or "Default",
        source=wrapped,
        terminal=False,
    ):
        dt_headers = [(k, v.encode("utf-8")) for k, v in MessageTrace.generate_request_headers(transaction)]
        # headers can be a list of tuples or a dict so convert to dict for consistency.
        if headers:
            dt_headers.extend(headers)

        try:
            return wrapped(
                topic, value=value, key=key, headers=dt_headers, partition=partition, timestamp_ms=timestamp_ms
            )
        except Exception:
            notice_error()
            raise


def wrap_kafkaconsumer_next(wrapped, instance, args, kwargs):
    if hasattr(instance, "_nr_transaction") and not instance._nr_transaction.stopped:
        instance._nr_transaction.__exit__(*sys.exc_info())

    try:
        record = wrapped(*args, **kwargs)
    except Exception as e:
        # StopIteration is an expected error, indicating the end of an iterable,
        # that should not be captured.
        if not isinstance(e, StopIteration):
            if current_transaction():
                # Report error on existing transaction if there is one
                notice_error()
            else:
                # Report error on application
                notice_error(application=application_instance(activate=False))
        raise

    if record:
        # This iterator can be called either outside of a transaction, or
        # within the context of an existing transaction.  There are 3
        # possibilities we need to handle: (Note that this is similar to
        # our Pika and Celery instrumentation)
        #
        #   1. In an inactive transaction
        #
        #      If the end_of_transaction() or ignore_transaction() API
        #      calls have been invoked, this iterator may be called in the
        #      context of an inactive transaction. In this case, don't wrap
        #      the iterator in any way. Just run the original iterator.
        #
        #   2. In an active transaction
        #
        #      Do nothing.
        #
        #   3. Outside of a transaction
        #
        #      Since it's not running inside of an existing transaction, we
        #      want to create a new background transaction for it.

        library = "Kafka"
        destination_type = "Topic"
        destination_name = record.topic
        received_bytes = len(str(record.value).encode("utf-8"))
        message_count = 1

        transaction = current_transaction(active_only=False)

        if not transaction:
            transaction = MessageTransaction(
                application=application_instance(),
                library=library,
                destination_type=destination_type,
                destination_name=destination_name,
                headers=dict(record.headers),
                transport_type="Kafka",
                routing_key=record.key,
                source=wrapped,
            )
            instance._nr_transaction = transaction
            transaction.__enter__()  # pylint: disable=C2801

            # Obtain consumer client_id to send up as agent attribute
            if hasattr(instance, "config") and "client_id" in instance.config:
                client_id = instance.config["client_id"]
                transaction._add_agent_attribute("kafka.consume.client_id", client_id)

            transaction._add_agent_attribute("kafka.consume.byteCount", received_bytes)

        transaction = current_transaction()
        if transaction:  # If there is an active transaction now.
            # Add metrics whether or not a transaction was already active, or one was just started.
            # Don't add metrics if there was an inactive transaction.
            # Name the metrics using the same format as the transaction, but in case the active transaction
            # was an existing one and not a message transaction, reproduce the naming logic here.
            group = "Message/%s/%s" % (library, destination_type)
            name = "Named/%s" % destination_name
            transaction.record_custom_metric("%s/%s/Received/Bytes" % (group, name), received_bytes)
            transaction.record_custom_metric("%s/%s/Received/Messages" % (group, name), message_count)
            transaction.add_messagebroker_info("Kafka-Python", get_package_version("kafka-python"))

    return record


def wrap_KafkaProducer_init(wrapped, instance, args, kwargs):
    get_config_key = lambda key: kwargs.get(key, instance.DEFAULT_CONFIG[key])  # pylint: disable=C3001 # noqa: E731

    kwargs["key_serializer"] = wrap_serializer(
        instance, "Serialization/Key", "MessageBroker", get_config_key("key_serializer")
    )
    kwargs["value_serializer"] = wrap_serializer(
        instance, "Serialization/Value", "MessageBroker", get_config_key("value_serializer")
    )

    return wrapped(*args, **kwargs)


class NewRelicSerializerWrapper(ObjectProxy):
    def __init__(self, wrapped, serializer_name, group_prefix):
        ObjectProxy.__init__.__get__(self)(wrapped)  # pylint: disable=W0231

        self._nr_serializer_name = serializer_name
        self._nr_group_prefix = group_prefix

    def serialize(self, topic, object):
        wrapped = self.__wrapped__.serialize  # pylint: disable=W0622
        args = (topic, object)
        kwargs = {}

        if not current_transaction():
            return wrapped(*args, **kwargs)

        group = "%s/Kafka/Topic" % self._nr_group_prefix
        name = "Named/%s/%s" % (topic, self._nr_serializer_name)

        return FunctionTraceWrapper(wrapped, name=name, group=group)(*args, **kwargs)


def wrap_serializer(client, serializer_name, group_prefix, serializer):
    @function_wrapper
    def _wrap_serializer(wrapped, instance, args, kwargs):
        transaction = current_transaction()
        if not transaction:
            return wrapped(*args, **kwargs)

        topic = "Unknown"
        if isinstance(transaction, MessageTransaction):
            topic = transaction.destination_name
        else:
            # Find parent message trace to retrieve topic
            message_trace = current_trace()
            while message_trace is not None and not isinstance(message_trace, MessageTrace):
                message_trace = message_trace.parent
            if message_trace:
                topic = message_trace.destination_name

        group = "%s/Kafka/Topic" % group_prefix
        name = "Named/%s/%s" % (topic, serializer_name)

        return FunctionTraceWrapper(wrapped, name=name, group=group)(*args, **kwargs)

    try:
        # Apply wrapper to serializer
        if serializer is None:
            # Do nothing
            return serializer
        elif isinstance(serializer, Serializer):
            return NewRelicSerializerWrapper(serializer, group_prefix=group_prefix, serializer_name=serializer_name)
        else:
            # Wrap callable in wrapper
            return _wrap_serializer(serializer)
    except Exception:
        return serializer  # Avoid crashes from immutable serializers


def metric_wrapper(metric_name, check_result=False):
    def _metric_wrapper(wrapped, instance, args, kwargs):
        result = wrapped(*args, **kwargs)

        application = application_instance(activate=False)
        if application:
            if not check_result or check_result and result:
                # If the result does not need validated, send metric.
                # If the result does need validated, ensure it is True.
                application.record_custom_metric(metric_name, 1)

        return result

    return _metric_wrapper


def instrument_kafka_producer(module):
    if hasattr(module, "KafkaProducer"):
        wrap_function_wrapper(module, "KafkaProducer.__init__", wrap_KafkaProducer_init)
        wrap_function_wrapper(module, "KafkaProducer.send", wrap_KafkaProducer_send)


def instrument_kafka_consumer_group(module):
    if hasattr(module, "KafkaConsumer"):
        wrap_function_wrapper(module, "KafkaConsumer.__next__", wrap_kafkaconsumer_next)


def instrument_kafka_heartbeat(module):
    if hasattr(module, "Heartbeat"):
        if hasattr(module.Heartbeat, "poll"):
            wrap_function_wrapper(module, "Heartbeat.poll", metric_wrapper(HEARTBEAT_POLL))

        if hasattr(module.Heartbeat, "fail_heartbeat"):
            wrap_function_wrapper(module, "Heartbeat.fail_heartbeat", metric_wrapper(HEARTBEAT_FAIL))

        if hasattr(module.Heartbeat, "sent_heartbeat"):
            wrap_function_wrapper(module, "Heartbeat.sent_heartbeat", metric_wrapper(HEARTBEAT_SENT))

        if hasattr(module.Heartbeat, "received_heartbeat"):
            wrap_function_wrapper(module, "Heartbeat.received_heartbeat", metric_wrapper(HEARTBEAT_RECEIVE))

        if hasattr(module.Heartbeat, "session_timeout_expired"):
            wrap_function_wrapper(
                module,
                "Heartbeat.session_timeout_expired",
                metric_wrapper(HEARTBEAT_SESSION_TIMEOUT, check_result=True),
            )

        if hasattr(module.Heartbeat, "poll_timeout_expired"):
            wrap_function_wrapper(
                module, "Heartbeat.poll_timeout_expired", metric_wrapper(HEARTBEAT_POLL_TIMEOUT, check_result=True)
            )
