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

"""
This module provides common utilities for interacting with OTLP protocol buffers.

The serialization implemented here attempts to use protobuf as an encoding, but falls
back to JSON when encoutering exceptions unless the content type is explicitly set in debug settings.
"""

import logging

from newrelic.common.encoding_utils import json_encode
from newrelic.core.config import global_settings
from newrelic.core.stats_engine import CountStats, TimeStats

_logger = logging.getLogger(__name__)

_settings = global_settings()
otlp_content_setting = _settings.debug.otlp_content_encoding
if not otlp_content_setting or otlp_content_setting == "protobuf":
    try:
        from newrelic.packages.opentelemetry_proto.common_pb2 import AnyValue, KeyValue
        from newrelic.packages.opentelemetry_proto.logs_pb2 import (
            LogsData,
            ResourceLogs,
            ScopeLogs,
        )
        from newrelic.packages.opentelemetry_proto.metrics_pb2 import (
            AggregationTemporality,
            Metric,
            MetricsData,
            NumberDataPoint,
            ResourceMetrics,
            ScopeMetrics,
            Sum,
            Summary,
            SummaryDataPoint,
        )
        from newrelic.packages.opentelemetry_proto.resource_pb2 import Resource

        ValueAtQuantile = SummaryDataPoint.ValueAtQuantile
        AGGREGATION_TEMPORALITY_DELTA = AggregationTemporality.AGGREGATION_TEMPORALITY_DELTA
        OTLP_CONTENT_TYPE = "application/x-protobuf"

        otlp_content_setting = "protobuf"  # Explicitly set to overwrite None values
    except Exception:
        if otlp_content_setting == "protobuf":
            raise  # Reraise exception if content type explicitly set
        # Fallback to JSON
        otlp_content_setting = "json"


if otlp_content_setting == "json":
    AnyValue = dict
    KeyValue = dict
    Metric = dict
    MetricsData = dict
    NumberDataPoint = dict
    Resource = dict
    ResourceMetrics = dict
    ScopeMetrics = dict
    Sum = dict
    Summary = dict
    SummaryDataPoint = dict
    ValueAtQuantile = dict
    ResourceLogs = dict
    ScopeLogs = dict
    LogsData = dict

    AGGREGATION_TEMPORALITY_DELTA = 1
    OTLP_CONTENT_TYPE = "application/json"


def otlp_encode(payload):
    if type(payload) is dict:  # pylint: disable=C0123
        _logger.warning(
            "Using OTLP integration while protobuf is not installed. This may result in larger payload sizes and data loss."
        )
        return json_encode(payload).encode("utf-8")
    return payload.SerializeToString()


def create_key_value(key, value):
    if isinstance(value, bool):
        return KeyValue(key=key, value=AnyValue(bool_value=value))
    elif isinstance(value, int):
        return KeyValue(key=key, value=AnyValue(int_value=value))
    elif isinstance(value, float):
        return KeyValue(key=key, value=AnyValue(double_value=value))
    elif isinstance(value, str):
        return KeyValue(key=key, value=AnyValue(string_value=value))
    # Technically AnyValue accepts array, kvlist, and bytes however, since
    # those are not valid custom attribute types according to our api spec,
    # we will not bother to support them here either.
    else:
        _logger.warning("Unsupported attribute value type %s: %s." % (key, value))


def create_key_values_from_iterable(iterable):
    if not iterable:
        return None
    elif isinstance(iterable, dict):
        iterable = iterable.items()

    # The create_key_value list may return None if the value is an unsupported type
    # so filter None values out before returning.
    return list(
        filter(
            lambda i: i is not None,
            (create_key_value(key, value) for key, value in iterable),
        )
    )


def create_resource(attributes=None):
    attributes = attributes or {"instrumentation.provider": "newrelic-opentelemetry-python-ml"}
    return Resource(attributes=create_key_values_from_iterable(attributes))


def TimeStats_to_otlp_data_point(self, start_time, end_time, attributes=None):
    data = SummaryDataPoint(
        time_unix_nano=int(end_time * 1e9),  # Time of current harvest
        start_time_unix_nano=int(start_time * 1e9),  # Time of last harvest
        attributes=attributes,
        count=int(self[0]),
        sum=float(self[1]),
        quantile_values=[
            ValueAtQuantile(quantile=0.0, value=float(self[3])),  # Min Value
            ValueAtQuantile(quantile=1.0, value=float(self[4])),  # Max Value
        ],
    )
    return data


def CountStats_to_otlp_data_point(self, start_time, end_time, attributes=None):
    data = NumberDataPoint(
        time_unix_nano=int(end_time * 1e9),  # Time of current harvest
        start_time_unix_nano=int(start_time * 1e9),  # Time of last harvest
        attributes=attributes,
        as_int=int(self[0]),
    )
    return data


def stats_to_otlp_metrics(metric_data, start_time, end_time):
    """
    Generator producing protos for Summary and Sum metrics, for CountStats and TimeStats respectively.

    Individual Metric protos must be entirely one type of metric data point. For mixed metric types we have to
    separate the types and report multiple metrics, one for each type.
    """
    for name, metric_container in metric_data:
        # Types are checked here using type() instead of isinstance, as CountStats is a subclass of TimeStats.
        # Imporperly checking with isinstance will lead to count metrics being encoded and reported twice.
        if any(type(metric) is CountStats for metric in metric_container.values()):  # pylint: disable=C0123
            # Metric contains Sum metric data points.
            yield Metric(
                name=name,
                sum=Sum(
                    aggregation_temporality=AGGREGATION_TEMPORALITY_DELTA,
                    is_monotonic=True,
                    data_points=[
                        CountStats_to_otlp_data_point(
                            value,
                            start_time=start_time,
                            end_time=end_time,
                            attributes=create_key_values_from_iterable(tags),
                        )
                        for tags, value in metric_container.items()
                        if type(value) is CountStats  # pylint: disable=C0123
                    ],
                ),
            )
        if any(type(metric) is TimeStats for metric in metric_container.values()):  # pylint: disable=C0123
            # Metric contains Summary metric data points.
            yield Metric(
                name=name,
                summary=Summary(
                    data_points=[
                        TimeStats_to_otlp_data_point(
                            value,
                            start_time=start_time,
                            end_time=end_time,
                            attributes=create_key_values_from_iterable(tags),
                        )
                        for tags, value in metric_container.items()
                        if type(value) is TimeStats  # pylint: disable=C0123
                    ]
                ),
            )


def encode_metric_data(metric_data, start_time, end_time, resource=None, scope=None):
    resource = resource or create_resource()
    return MetricsData(
        resource_metrics=[
            ResourceMetrics(
                resource=resource,
                scope_metrics=[
                    ScopeMetrics(
                        scope=scope,
                        metrics=list(stats_to_otlp_metrics(metric_data, start_time, end_time)),
                    )
                ],
            )
        ]
    )


def encode_ml_event_data(custom_event_data, agent_run_id):
    resource = create_resource()
    ml_events = []
    for event in custom_event_data:
        event_info, event_attrs = event
        event_attrs.update(
            {
                "real_agent_id": agent_run_id,
                "event.domain": "newrelic.ml_events",
                "event.name": event_info["type"],
            }
        )
        ml_attrs = create_key_values_from_iterable(event_attrs)
        unix_nano_timestamp = event_info["timestamp"] * 1e6
        ml_events.append(
            {
                "time_unix_nano": int(unix_nano_timestamp),
                "attributes": ml_attrs,
            }
        )

    return LogsData(resource_logs=[ResourceLogs(resource=resource, scope_logs=[ScopeLogs(log_records=ml_events)])])
