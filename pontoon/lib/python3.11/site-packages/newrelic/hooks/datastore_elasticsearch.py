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

from newrelic.api.datastore_trace import DatastoreTrace
from newrelic.api.transaction import current_transaction
from newrelic.common.object_wrapper import function_wrapper, wrap_function_wrapper
from newrelic.common.package_version_utils import get_package_version_tuple
from newrelic.packages import six

# An index name can be a string, None or a sequence. In the case of None
# an empty string or '*', it is the same as using '_all'. When a string
# it can also be a comma separated list of index names. A sequence
# obviously can also be more than one index name. Where we are certain
# there is only a single index name we use it, otherwise we use 'other'.

ES_VERSION = get_package_version_tuple("elasticsearch")


def _index_name(index):
    if not index or index == "*":
        return "_all"
    if not isinstance(index, six.string_types) or "," in index:
        return "other"
    return index


def _extract_args_index(index=None, *args, **kwargs):
    return _index_name(index)


def _extract_args_allocation_explain_index(
    current_node=None,
    error_trace=None,
    filter_path=None,
    human=None,
    include_disk_info=None,
    include_yes_decisions=None,
    index=None,
    *args,
    **kwargs
):
    return _index_name(index)


def _extract_args_name_index(name=None, index=None, *args, **kwargs):
    return _index_name(index)


def _extract_args_body_index(body=None, index=None, *args, **kwargs):
    return _index_name(index)


def _extract_args_requests_index(requests=None, index=None, *args, **kwargs):
    return _index_name(index)


def _extract_args_searches_index(searches=None, index=None, *args, **kwargs):
    return _index_name(index)


def _extract_args_search_templates_index(search_templates=None, index=None, *args, **kwargs):
    return _index_name(index)


def _extract_args_operations_index(operations=None, index=None, *args, **kwargs):
    return _index_name(index)


def _extract_args_doctype_body_index(doc_type=None, body=None, index=None, *args, **kwargs):
    return _index_name(index)


def _extract_args_field_index(field=None, index=None, *args, **kwargs):
    return _index_name(index)


def _extract_args_fields_index(fields=None, index=None, *args, **kwargs):
    return _index_name(index)


def _extract_args_name_body_index(name=None, body=None, index=None, *args, **kwargs):
    return _index_name(index)


def _extract_args_metric_index(metric=None, index=None, *args, **kwargs):
    return _index_name(index)


def _extract_args_settings_index(settings=None, index=None, *args, **kwargs):
    return _index_name(index)


def instrument_es_methods(module, _class, client_methods, prefix=None):
    for method_name, arg_extractor in client_methods:
        if hasattr(getattr(module, _class), method_name):
            wrap_elasticsearch_client_method(module, _class, method_name, arg_extractor, prefix)


def wrap_elasticsearch_client_method(module, class_name, method_name, arg_extractor, prefix=None):
    def _nr_wrapper_Elasticsearch_method_(wrapped, instance, args, kwargs):
        transaction = current_transaction()

        if transaction is None:
            return wrapped(*args, **kwargs)
        # When index is None, it means there is no target field
        # associated with this method. Hence this method will only
        # create an operation metric and no statement metric. This is
        # handled by setting the target to None when calling the
        # DatastoreTraceWrapper.
        if arg_extractor is None:
            index = None
        else:
            index = arg_extractor(*args, **kwargs)

        if prefix:
            operation = "%s.%s" % (prefix, method_name)
        else:
            operation = method_name

        transaction._nr_datastore_instance_info = (None, None, None)

        dt = DatastoreTrace(product="Elasticsearch", target=index, operation=operation, source=wrapped)

        with dt:
            result = wrapped(*args, **kwargs)

            instance_info = transaction._nr_datastore_instance_info
            host, port_path_or_id, _ = instance_info

            dt.host = host
            dt.port_path_or_id = port_path_or_id

            return result

    wrap_function_wrapper(module, "%s.%s" % (class_name, method_name), _nr_wrapper_Elasticsearch_method_)


_elasticsearch_client_methods_below_v8 = (
    ("abort_benchmark", None),
    ("benchmark", _extract_args_index),
    ("bulk", None),
    ("clear_scroll", None),
    ("count", _extract_args_index),
    ("count_percolate", _extract_args_index),
    ("create", _extract_args_index),
    ("delete", _extract_args_index),
    ("delete_by_query", _extract_args_index),
    ("delete_script", None),
    ("delete_template", None),
    ("exists", _extract_args_index),
    ("explain", _extract_args_index),
    ("get", _extract_args_index),
    ("get_script", None),
    ("get_source", _extract_args_index),
    ("get_template", None),
    ("index", _extract_args_index),
    ("info", None),
    ("list_benchmarks", _extract_args_index),
    ("mget", None),
    ("mlt", _extract_args_index),
    ("mpercolate", _extract_args_body_index),
    ("msearch", None),
    ("mtermvectors", None),
    ("percolate", _extract_args_index),
    ("ping", None),
    ("put_script", None),
    ("put_template", None),
    ("scroll", None),
    ("search", _extract_args_index),
    ("search_exists", _extract_args_index),
    ("search_shards", _extract_args_index),
    ("search_template", _extract_args_index),
    ("suggest", _extract_args_body_index),
    ("termvector", _extract_args_index),
    ("termvectors", None),
    ("update", _extract_args_index),
)


_elasticsearch_client_methods_v8 = (
    ("bulk", _extract_args_operations_index),
    ("clear_scroll", None),
    ("close", None),
    ("close_point_in_time", None),
    ("count", _extract_args_index),
    ("create", _extract_args_index),
    ("delete", _extract_args_index),
    ("delete_by_query", _extract_args_index),
    ("delete_by_query_rethrottle", None),
    ("delete_script", None),
    ("exists", _extract_args_index),
    ("exists_source", _extract_args_index),
    ("explain", _extract_args_index),
    ("field_caps", _extract_args_index),
    ("get", _extract_args_index),
    ("get_script", None),
    ("get_script_context", None),
    ("get_script_languages", None),
    ("get_source", _extract_args_index),
    ("index", _extract_args_index),
    ("info", None),
    ("knn_search", _extract_args_index),
    ("mget", _extract_args_index),
    ("msearch", _extract_args_searches_index),
    ("msearch_template", _extract_args_search_templates_index),
    ("mtermvectors", _extract_args_index),
    ("open_point_in_time", _extract_args_index),
    ("options", None),
    ("ping", None),
    ("put_script", None),
    ("rank_eval", _extract_args_requests_index),
    ("reindex", None),
    ("reindex_rethrottle", None),
    ("render_search_template", None),
    ("scripts_painless_execute", None),
    ("scroll", None),
    ("search", _extract_args_index),
    ("search_mvt", _extract_args_index),
    ("search_shards", _extract_args_index),
    ("terms_enum", _extract_args_index),
    ("termvector", _extract_args_index),
    ("termvectors", _extract_args_index),
    ("update", _extract_args_index),
    ("update_by_query", _extract_args_index),
    ("update_by_query_rethrottle", None),
)


def instrument_elasticsearch_client(module):
    # The module path was remapped in v8 to match previous versions.
    # In order to avoid double wrapping we check the version before
    # wrapping.
    if ES_VERSION < (8,):
        instrument_es_methods(module, "Elasticsearch", _elasticsearch_client_methods_below_v8)


def instrument_elasticsearch_client_v8(module):
    instrument_es_methods(module, "Elasticsearch", _elasticsearch_client_methods_v8)


_elasticsearch_client_indices_methods_below_v8 = (
    ("analyze", _extract_args_index),
    ("clear_cache", _extract_args_index),
    ("close", _extract_args_index),
    ("create", _extract_args_index),
    ("delete", _extract_args_index),
    ("delete_alias", _extract_args_index),
    ("delete_mapping", _extract_args_index),
    ("delete_template", None),
    ("delete_warmer", _extract_args_index),
    ("exists", _extract_args_index),
    ("exists_alias", _extract_args_name_index),
    ("exists_template", None),
    ("exists_type", _extract_args_index),
    ("flush", _extract_args_index),
    ("get", _extract_args_index),
    ("get_alias", _extract_args_index),
    ("get_aliases", _extract_args_index),
    ("get_mapping", _extract_args_index),
    ("get_field_mapping", _extract_args_field_index),
    ("get_settings", _extract_args_index),
    ("get_template", None),
    ("get_upgrade", _extract_args_index),
    ("get_warmer", _extract_args_index),
    ("open", _extract_args_index),
    ("optimize", _extract_args_index),
    ("put_alias", _extract_args_name_index),
    ("put_mapping", _extract_args_doctype_body_index),
    ("put_settings", _extract_args_body_index),
    ("put_template", None),
    ("put_warmer", _extract_args_name_body_index),
    ("recovery", _extract_args_index),
    ("refresh", _extract_args_index),
    ("segments", _extract_args_index),
    ("snapshot_index", _extract_args_index),
    ("stats", _extract_args_index),
    ("status", _extract_args_index),
    ("update_aliases", None),
    ("upgrade", _extract_args_index),
    ("validate_query", _extract_args_index),
)


_elasticsearch_client_indices_methods_v8 = (
    ("add_block", _extract_args_index),
    ("analyze", _extract_args_index),
    ("clear_cache", _extract_args_index),
    ("clone", _extract_args_index),
    ("close", _extract_args_index),
    ("create", _extract_args_index),
    ("create_data_stream", None),
    ("data_streams_stats", None),
    ("delete", _extract_args_index),
    ("delete_alias", _extract_args_index),
    ("delete_data_stream", None),
    ("delete_index_template", None),
    ("delete_template", None),
    ("disk_usage", _extract_args_index),
    ("downsample", _extract_args_index),
    ("exists", _extract_args_index),
    ("exists_alias", _extract_args_name_index),
    ("exists_index_template", None),
    ("exists_template", None),
    ("field_usage_stats", _extract_args_index),
    ("flush", _extract_args_index),
    ("forcemerge", _extract_args_index),
    ("get", _extract_args_index),
    ("get_alias", _extract_args_index),
    ("get_data_stream", None),
    ("get_field_mapping", _extract_args_fields_index),
    ("get_index_template", None),
    ("get_mapping", _extract_args_index),
    ("get_settings", _extract_args_index),
    ("get_template", None),
    ("migrate_to_data_stream", None),
    ("modify_data_stream", None),
    ("open", _extract_args_index),
    ("promote_data_stream", None),
    ("put_alias", _extract_args_index),
    ("put_index_template", None),
    ("put_mapping", _extract_args_index),
    ("put_settings", _extract_args_settings_index),
    ("put_template", None),
    ("recovery", _extract_args_index),
    ("refresh", _extract_args_index),
    ("reload_search_analyzers", _extract_args_index),
    ("resolve_index", None),
    ("rollover", None),
    ("segments", _extract_args_index),
    ("shard_stores", _extract_args_index),
    ("shrink", _extract_args_index),
    ("simulate_index_template", None),
    ("simulate_template", None),
    ("split", _extract_args_index),
    ("stats", _extract_args_index),
    ("unfreeze", _extract_args_index),
    ("update_aliases", None),
    ("validate_query", _extract_args_index),
)


def instrument_elasticsearch_client_indices(module):
    # The module path was remapped in v8 to match previous versions.
    # In order to avoid double wrapping we check the version before
    # wrapping.
    if ES_VERSION < (8,):
        instrument_es_methods(module, "IndicesClient", _elasticsearch_client_indices_methods_below_v8, "indices")


def instrument_elasticsearch_client_indices_v8(module):
    instrument_es_methods(module, "IndicesClient", _elasticsearch_client_indices_methods_v8, "indices")


_elasticsearch_client_cat_methods_below_v8 = (
    ("aliases", None),
    ("allocation", None),
    ("count", _extract_args_index),
    ("fielddata", None),
    ("health", None),
    ("help", None),
    ("indices", _extract_args_index),
    ("master", None),
    ("nodes", None),
    ("pending_tasks", None),
    ("plugins", None),
    ("recovery", _extract_args_index),
    ("shards", _extract_args_index),
    ("segments", _extract_args_index),
    ("thread_pool", None),
)

_elasticsearch_client_cat_methods_v8 = (
    ("aliases", None),
    ("allocation", None),
    ("component_templates", None),
    ("count", _extract_args_index),
    ("fielddata", None),
    ("health", None),
    ("help", None),
    ("indices", _extract_args_index),
    ("master", None),
    ("ml_data_frame_analytics", None),
    ("ml_datafeeds", None),
    ("ml_jobs", None),
    ("ml_trained_models", None),
    ("nodeattrs", None),
    ("nodes", None),
    ("pending_tasks", None),
    ("plugins", None),
    ("recovery", _extract_args_index),
    ("repositories", None),
    ("segments", _extract_args_index),
    ("shards", _extract_args_index),
    ("snapshots", None),
    ("tasks", None),
    ("templates", None),
    ("thread_pool", None),
    ("transforms", None),
)


def instrument_elasticsearch_client_cat(module):
    # The module path was remapped in v8 to match previous versions.
    # In order to avoid double wrapping we check the version before
    # wrapping.
    if ES_VERSION < (8,):
        instrument_es_methods(module, "CatClient", _elasticsearch_client_cat_methods_below_v8, "cat")


def instrument_elasticsearch_client_cat_v8(module):
    instrument_es_methods(module, "CatClient", _elasticsearch_client_cat_methods_v8, "cat")


_elasticsearch_client_cluster_methods_below_v8 = (
    ("get_settings", None),
    ("health", _extract_args_index),
    ("pending_tasks", None),
    ("put_settings", None),
    ("reroute", None),
    ("state", _extract_args_metric_index),
    ("stats", None),
)


_elasticsearch_client_cluster_methods_v8 = (
    ("allocation_explain", _extract_args_allocation_explain_index),
    ("delete_component_template", None),
    ("delete_voting_config_exclusions", None),
    ("exists_component_template", None),
    ("get_component_template", None),
    ("get_settings", None),
    ("health", _extract_args_index),
    ("pending_tasks", None),
    ("post_voting_config_exclusions", None),
    ("put_component_template", None),
    ("put_settings", None),
    ("remote_info", None),
    ("reroute", None),
    ("state", _extract_args_metric_index),
    ("stats", None),
)


def instrument_elasticsearch_client_cluster(module):
    # The module path was remapped in v8 to match previous versions.
    # In order to avoid double wrapping we check the version before
    # wrapping.
    if ES_VERSION < (8,):
        instrument_es_methods(module, "ClusterClient", _elasticsearch_client_cluster_methods_below_v8, "cluster")


def instrument_elasticsearch_client_cluster_v8(module):
    instrument_es_methods(module, "ClusterClient", _elasticsearch_client_cluster_methods_v8, "cluster")


_elasticsearch_client_nodes_methods_below_v8 = (
    ("hot_threads", None),
    ("info", None),
    ("shutdown", None),
    ("stats", None),
)
_elasticsearch_client_nodes_methods_v8 = (
    ("clear_repositories_metering_archive", None),
    ("get_repositories_metering_info", None),
    ("hot_threads", None),
    ("info", None),
    ("reload_secure_settings", None),
    ("stats", None),
    ("usage", None),
)


def instrument_elasticsearch_client_nodes(module):
    # The module path was remapped in v8 to match previous versions.
    # In order to avoid double wrapping we check the version before
    # wrapping.
    if ES_VERSION < (8,):
        instrument_es_methods(module, "NodesClient", _elasticsearch_client_nodes_methods_below_v8, "nodes")


def instrument_elasticsearch_client_nodes_v8(module):
    instrument_es_methods(module, "NodesClient", _elasticsearch_client_nodes_methods_v8, "nodes")


_elasticsearch_client_snapshot_methods_below_v8 = (
    ("create", None),
    ("create_repository", None),
    ("delete", None),
    ("delete_repository", None),
    ("get", None),
    ("get_repository", None),
    ("restore", None),
    ("status", None),
    ("verify_repository", None),
)
_elasticsearch_client_snapshot_methods_v8 = (
    ("cleanup_repository", None),
    ("clone", None),
    ("create", None),
    ("create_repository", None),
    ("delete", None),
    ("delete_repository", None),
    ("get", None),
    ("get_repository", None),
    ("restore", None),
    ("status", None),
    ("verify_repository", None),
)


def instrument_elasticsearch_client_snapshot(module):
    # The module path was remapped in v8 to match previous versions.
    # In order to avoid double wrapping we check the version before
    # wrapping.
    if ES_VERSION < (8,):
        instrument_es_methods(module, "SnapshotClient", _elasticsearch_client_snapshot_methods_below_v8, "snapshot")


def instrument_elasticsearch_client_snapshot_v8(module):
    instrument_es_methods(module, "SnapshotClient", _elasticsearch_client_snapshot_methods_v8, "snapshot")


_elasticsearch_client_tasks_methods = (
    ("list", None),
    ("cancel", None),
    ("get", None),
)


def instrument_elasticsearch_client_tasks(module):
    # The module path was remapped in v8 to match previous versions.
    # In order to avoid double wrapping we check the version before
    # wrapping.
    if ES_VERSION < (8,):
        instrument_es_methods(module, "TasksClient", _elasticsearch_client_tasks_methods, "tasks")


def instrument_elasticsearch_client_tasks_v8(module):
    instrument_es_methods(module, "TasksClient", _elasticsearch_client_tasks_methods, "tasks")


_elasticsearch_client_ingest_methods_below_v8 = (
    ("get_pipeline", None),
    ("put_pipeline", None),
    ("delete_pipeline", None),
    ("simulate", None),
)

_elasticsearch_client_ingest_methods_v8 = (
    ("delete_pipeline", None),
    ("geo_ip_stats", None),
    ("get_pipeline", None),
    ("processor_grok", None),
    ("put_pipeline", None),
    ("simulate", None),
)


def instrument_elasticsearch_client_ingest(module):
    # The module path was remapped in v8 to match previous versions.
    # In order to avoid double wrapping we check the version before
    # wrapping.
    if ES_VERSION < (8,):
        instrument_es_methods(module, "IngestClient", _elasticsearch_client_ingest_methods_below_v8, "ingest")


def instrument_elasticsearch_client_ingest_v8(module):
    instrument_es_methods(module, "IngestClient", _elasticsearch_client_ingest_methods_v8, "ingest")


#
# Instrumentation to get Datastore Instance Information
#


def _nr_Connection__init__wrapper(wrapped, instance, args, kwargs):
    """Cache datastore instance info on Connection object"""

    def _bind_params(host="localhost", port=9200, *args, **kwargs):
        return host, port

    host, port = _bind_params(*args, **kwargs)
    port = str(port)
    instance._nr_host_port = (host, port)

    return wrapped(*args, **kwargs)


def instrument_elasticsearch_connection_base(module):
    wrap_function_wrapper(module, "Connection.__init__", _nr_Connection__init__wrapper)


def BaseNode__init__wrapper(wrapped, instance, args, kwargs):
    result = wrapped(*args, **kwargs)
    instance._nr_host_port = (instance.host, str(instance.port))
    return result


def instrument_elastic_transport__node__base(module):
    if hasattr(module, "BaseNode"):
        wrap_function_wrapper(module, "BaseNode.__init__", BaseNode__init__wrapper)


def _nr_get_connection_wrapper(wrapped, instance, args, kwargs):
    """Read instance info from Connection and stash on Transaction."""

    transaction = current_transaction()

    if transaction is None:
        return wrapped(*args, **kwargs)

    conn = wrapped(*args, **kwargs)

    instance_info = (None, None, None)
    try:
        tracer_settings = transaction.settings.datastore_tracer

        if tracer_settings.instance_reporting.enabled:
            host, port_path_or_id = conn._nr_host_port
            instance_info = (host, port_path_or_id, None)
    except Exception:
        instance_info = ("unknown", "unknown", None)

    transaction._nr_datastore_instance_info = instance_info

    return conn


def _nr_perform_request_wrapper(wrapped, instance, args, kwargs):
    """Read instance info from Connection and stash on Transaction."""

    transaction = current_transaction()

    if transaction is None:
        return wrapped(*args, **kwargs)

    if not hasattr(instance.node_pool.get, "_nr_wrapped"):
        instance.node_pool.get = function_wrapper(_nr_get_connection_wrapper)(instance.node_pool.get)
        instance.node_pool.get._nr_wrapped = True

    return wrapped(*args, **kwargs)


def instrument_elasticsearch_transport(module):
    if hasattr(module, "Transport") and hasattr(module.Transport, "get_connection"):
        wrap_function_wrapper(module, "Transport.get_connection", _nr_get_connection_wrapper)


def instrument_elastic_transport__transport(module):
    if hasattr(module, "Transport") and hasattr(module.Transport, "perform_request"):
        wrap_function_wrapper(module, "Transport.perform_request", _nr_perform_request_wrapper)
