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
import sys

from newrelic.api.application import application_instance
from newrelic.api.error_trace import wrap_error_trace
from newrelic.api.function_trace import FunctionTraceWrapper
from newrelic.api.message_trace import MessageTrace
from newrelic.api.message_transaction import MessageTransaction
from newrelic.api.time_trace import notice_error
from newrelic.api.transaction import current_transaction
from newrelic.common.object_wrapper import function_wrapper, wrap_function_wrapper
from newrelic.common.package_version_utils import get_package_version

_logger = logging.getLogger(__name__)

HEARTBEAT_POLL = "MessageBroker/Kafka/Heartbeat/Poll"
HEARTBEAT_SENT = "MessageBroker/Kafka/Heartbeat/Sent"
HEARTBEAT_FAIL = "MessageBroker/Kafka/Heartbeat/Fail"
HEARTBEAT_RECEIVE = "MessageBroker/Kafka/Heartbeat/Receive"
HEARTBEAT_SESSION_TIMEOUT = "MessageBroker/Kafka/Heartbeat/SessionTimeout"
HEARTBEAT_POLL_TIMEOUT = "MessageBroker/Kafka/Heartbeat/PollTimeout"


def wrap_Producer_produce(wrapped, instance, args, kwargs):
    transaction = current_transaction()
    if transaction is None:
        return wrapped(*args, **kwargs)

    # Binding with a standard function signature does not work properly due to a bug in handling arguments
    # in the underlying C code, where callback=None being specified causes on_delivery=callback to never run.

    # Bind out headers from end of args list
    if len(args) == 8:
        # Take headers off the end of the positional args
        headers = args[7]
        args = args[0:7]
    else:
        headers = kwargs.pop("headers", [])

    # Bind topic off of the beginning of the args list
    if len(args) >= 1:
        topic = args[0]
        args = args[1:]
    else:
        topic = kwargs.pop("topic", None)

    transaction.add_messagebroker_info("Confluent-Kafka", get_package_version("confluent-kafka"))

    with MessageTrace(
        library="Kafka",
        operation="Produce",
        destination_type="Topic",
        destination_name=topic or "Default",
        source=wrapped,
    ):
        dt_headers = {k: v.encode("utf-8") for k, v in MessageTrace.generate_request_headers(transaction)}
        # headers can be a list of tuples or a dict so convert to dict for consistency.
        if headers:
            dt_headers.update(dict(headers))

        try:
            return wrapped(topic, headers=dt_headers, *args, **kwargs)
        except Exception as error:
            # Unwrap kafka errors
            while hasattr(error, "exception"):
                error = error.exception  # pylint: disable=E1101

            _, _, tb = sys.exc_info()
            notice_error((type(error), error, tb))
            tb = None  # Clear reference to prevent reference cycles
            raise


def wrap_Consumer_poll(wrapped, instance, args, kwargs):
    # This wrapper can be called either outside of a transaction, or
    # within the context of an existing transaction.  There are 4
    # possibilities we need to handle: (Note that this is similar to
    # our Pika, Celery, and Kafka-Python instrumentation)
    #
    #   1. Inside an inner wrapper in the DeserializingConsumer
    #
    #       Do nothing. The DeserializingConsumer is double wrapped because
    #       the underlying C implementation is wrapped as well. We need to
    #       detect when the second wrapper is called and ignore it completely
    #       or transactions will be stopped early.
    #
    #   2. In an inactive transaction
    #
    #      If the end_of_transaction() or ignore_transaction() API
    #      calls have been invoked, this iterator may be called in the
    #      context of an inactive transaction. In this case, don't wrap
    #      the iterator in any way. Just run the original iterator.
    #
    #   3. In an active transaction
    #
    #      Do nothing.
    #
    #   4. Outside of a transaction
    #
    #      Since it's not running inside of an existing transaction, we
    #      want to create a new background transaction for it.

    # Step 1: Stop existing transactions
    if hasattr(instance, "_nr_transaction") and not instance._nr_transaction.stopped:
        instance._nr_transaction.__exit__(*sys.exc_info())

    # Step 2: Poll for records
    try:
        record = wrapped(*args, **kwargs)
    except Exception as e:
        if current_transaction():
            notice_error()
        else:
            notice_error(application=application_instance(activate=False))
        raise

    # Step 3: Start new transaction for received record
    if record:
        library = "Kafka"
        destination_type = "Topic"
        destination_name = record.topic()
        received_bytes = len(str(record.value()).encode("utf-8"))
        message_count = 1

        headers = record.headers()
        headers = dict(headers) if headers else {}

        transaction = current_transaction(active_only=False)
        if not transaction:
            transaction = MessageTransaction(
                application=application_instance(),
                library=library,
                destination_type=destination_type,
                destination_name=destination_name,
                headers=headers,
                transport_type="Kafka",
                routing_key=record.key(),
                source=wrapped,
            )
            instance._nr_transaction = transaction
            transaction.__enter__()  # pylint: disable=C2801

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
            transaction.add_messagebroker_info("Confluent-Kafka", get_package_version("confluent-kafka"))

    return record


def wrap_DeserializingConsumer_poll(wrapped, instance, args, kwargs):
    try:
        return wrapped(*args, **kwargs)
    except Exception:
        notice_error()

        # Stop existing transactions
        if hasattr(instance, "_nr_transaction") and not instance._nr_transaction.stopped:
            instance._nr_transaction.__exit__(*sys.exc_info())

        raise


def wrap_serializer(serializer_name, group_prefix):
    @function_wrapper
    def _wrap_serializer(wrapped, instance, args, kwargs):
        if not current_transaction():
            return wrapped(*args, **kwargs)

        topic = args[1].topic
        group = "%s/Kafka/Topic" % group_prefix
        name = "Named/%s/%s" % (topic, serializer_name)

        return FunctionTraceWrapper(wrapped, name=name, group=group)(*args, **kwargs)

    return _wrap_serializer


def wrap_SerializingProducer_init(wrapped, instance, args, kwargs):
    wrapped(*args, **kwargs)

    if hasattr(instance, "_key_serializer") and callable(instance._key_serializer):
        instance._key_serializer = wrap_serializer("Serialization/Key", "MessageBroker")(instance._key_serializer)

    if hasattr(instance, "_value_serializer") and callable(instance._value_serializer):
        instance._value_serializer = wrap_serializer("Serialization/Value", "MessageBroker")(instance._value_serializer)


def wrap_DeserializingConsumer_init(wrapped, instance, args, kwargs):
    wrapped(*args, **kwargs)

    if hasattr(instance, "_key_deserializer") and callable(instance._key_deserializer):
        instance._key_deserializer = wrap_serializer("Deserialization/Key", "Message")(instance._key_deserializer)

    if hasattr(instance, "_value_deserializer") and callable(instance._value_deserializer):
        instance._value_deserializer = wrap_serializer("Deserialization/Value", "Message")(instance._value_deserializer)


def wrap_immutable_class(module, class_name):
    # Wrap immutable binary extension class with a mutable Python subclass
    new_class = type(class_name, (getattr(module, class_name),), {})
    setattr(module, class_name, new_class)
    return new_class


def instrument_confluentkafka_cimpl(module):
    if hasattr(module, "Producer"):
        wrap_immutable_class(module, "Producer")
        wrap_function_wrapper(module, "Producer.produce", wrap_Producer_produce)

    if hasattr(module, "Consumer"):
        wrap_immutable_class(module, "Consumer")
        wrap_function_wrapper(module, "Consumer.poll", wrap_Consumer_poll)


def instrument_confluentkafka_serializing_producer(module):
    if hasattr(module, "SerializingProducer"):
        wrap_function_wrapper(module, "SerializingProducer.__init__", wrap_SerializingProducer_init)
        wrap_error_trace(module, "SerializingProducer.produce")


def instrument_confluentkafka_deserializing_consumer(module):
    if hasattr(module, "DeserializingConsumer"):
        wrap_function_wrapper(module, "DeserializingConsumer.__init__", wrap_DeserializingConsumer_init)
        wrap_function_wrapper(module, "DeserializingConsumer.poll", wrap_DeserializingConsumer_poll)
