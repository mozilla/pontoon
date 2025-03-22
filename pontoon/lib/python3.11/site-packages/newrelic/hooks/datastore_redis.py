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

import re

from newrelic.api.datastore_trace import DatastoreTrace, DatastoreTraceWrapper, wrap_datastore_trace
from newrelic.api.time_trace import current_trace
from newrelic.api.transaction import current_transaction
from newrelic.common.object_wrapper import wrap_function_wrapper
from newrelic.common.async_wrapper import coroutine_wrapper, async_generator_wrapper, generator_wrapper

_redis_client_sync_methods = {
    "acl_dryrun",
    "auth",
    "bgrewriteaof",
    "bitfield",
    "blmpop",
    "bzmpop",
    "client",
    "command",
    "command_docs",
    "command_getkeysandflags",
    "command_info",
    "debug_segfault",
    "expiretime",
    "failover",
    "hello",
    "latency_doctor",
    "latency_graph",
    "latency_histogram",
    "lcs",
    "lpop",
    "lpos",
    "memory_doctor",
    "memory_help",
    "monitor",
    "pexpiretime",
    "psetex",
    "psync",
    "pubsub",
    "renamenx",
    "rpop",
    "script_debug",
    "sentinel_ckquorum",
    "sentinel_failover",
    "sentinel_flushconfig",
    "sentinel_get_master_addr_by_name",
    "sentinel_master",
    "sentinel_masters",
    "sentinel_monitor",
    "sentinel_remove",
    "sentinel_reset",
    "sentinel_sentinels",
    "sentinel_set",
    "sentinel_slaves",
    "shutdown",
    "sort",
    "sort_ro",
    "spop",
    "srandmember",
    "unwatch",
    "watch",
    "zlexcount",
    "zrevrangebyscore",
}


_redis_client_async_methods = {
    "acl_cat",
    "acl_deluser",
    "acl_genpass",
    "acl_getuser",
    "acl_help",
    "acl_list",
    "acl_load",
    "acl_log_reset",
    "acl_log",
    "acl_save",
    "acl_setuser",
    "acl_users",
    "acl_whoami",
    "add_document_hash",
    "add_document",
    "add",
    "addnx",
    "aggregate",
    "aliasadd",
    "aliasdel",
    "aliasupdate",
    "alter_schema_add",
    "alter",
    "append",
    "arrappend",
    "arrindex",
    "arrinsert",
    "arrlen",
    "arrpop",
    "arrtrim",
    "bgsave",
    "bitcount",
    "bitfield_ro",
    "bitop_and",
    "bitop_not",
    "bitop_or",
    "bitop_xor",
    "bitop",
    "bitpos",
    "blmove",
    "blpop",
    "brpop",
    "brpoplpush",
    "byrank",
    "byrevrank",
    "bzpopmax",
    "bzpopmin",
    "card",
    "cdf",
    "clear",
    "client_getname",
    "client_getredir",
    "client_id",
    "client_info",
    "client_kill_filter",
    "client_kill",
    "client_list",
    "client_no_evict",
    "client_pause",
    "client_reply",
    "client_setinfo",
    "client_setname",
    "client_tracking",
    "client_trackinginfo",
    "client_unblock",
    "client_unpause",
    "cluster_add_slots",
    "cluster_addslots",
    "cluster_count_failure_report",
    "cluster_count_failure_reports",
    "cluster_count_key_in_slots",
    "cluster_countkeysinslot",
    "cluster_del_slots",
    "cluster_delslots",
    "cluster_failover",
    "cluster_forget",
    "cluster_get_keys_in_slot",
    "cluster_get_keys_in_slots",
    "cluster_info",
    "cluster_keyslot",
    "cluster_meet",
    "cluster_nodes",
    "cluster_replicate",
    "cluster_reset_all_nodes",
    "cluster_reset",
    "cluster_save_config",
    "cluster_set_config_epoch",
    "cluster_setslot",
    "cluster_slaves",
    "cluster_slots",
    "cluster",
    "command_count",
    "command_getkeys",
    "command_list",
    "command",
    "commit",
    "config_get",
    "config_resetstat",
    "config_rewrite",
    "config_set",
    "config",
    "copy",
    "count",
    "create_index",
    "create",
    "createrule",
    "dbsize",
    "debug_object",
    "debug_sleep",
    "debug",
    "decr",
    "decrby",
    "delete_document",
    "delete",
    "deleterule",
    "dict_add",
    "dict_del",
    "dict_dump",
    "drop_index",
    "dropindex",
    "dump",
    "echo",
    "eval_ro",
    "eval",
    "evalsha_ro",
    "evalsha",
    "execution_plan",
    "exists",
    "expire",
    "expireat",
    "explain_cli",
    "explain",
    "fcall_ro",
    "fcall",
    "flushall",
    "flushdb",
    "forget",
    "function_delete",
    "function_dump",
    "function_flush",
    "function_kill",
    "function_list",
    "function_load",
    "function_restore",
    "function_stats",
    "gears_refresh_cluster",
    "geoadd",
    "geodist",
    "geohash",
    "geopos",
    "georadius",
    "georadiusbymember",
    "geosearch",
    "geosearchstore",
    "get",
    "getbit",
    "getdel",
    "getex",
    "getrange",
    "getset",
    "hdel",
    "hexists",
    "hget",
    "hgetall",
    "hincrby",
    "hincrbyfloat",
    "hkeys",
    "hlen",
    "hmget",
    "hmset_dict",
    "hmset",
    "hrandfield",
    "hscan_iter",
    "hscan",
    "hset",
    "hsetnx",
    "hstrlen",
    "hvals",
    "incr",
    "incrby",
    "incrbyfloat",
    "info",
    "initbydim",
    "initbyprob",
    "insert",
    "insertnx",
    "keys",
    "lastsave",
    "latency_history",
    "latency_latest",
    "latency_reset",
    "lindex",
    "linsert",
    "list",
    "llen",
    "lmove",
    "lmpop",
    "loadchunk",
    "lolwut",
    "lpush",
    "lpushx",
    "lrange",
    "lrem",
    "lset",
    "ltrim",
    "madd",
    "max",
    "memory_malloc_stats",
    "memory_purge",
    "memory_stats",
    "memory_usage",
    "merge",
    "mexists",
    "mget",
    "migrate_keys",
    "migrate",
    "min",
    "module_list",
    "module_load",
    "module_loadex",
    "module_unload",
    "move",
    "mrange",
    "mrevrange",
    "mset",
    "msetnx",
    "numincrby",
    "object_encoding",
    "object_idletime",
    "object_refcount",
    "object",
    "objkeys",
    "objlen",
    "persist",
    "pexpire",
    "pexpireat",
    "pfadd",
    "pfcount",
    "pfmerge",
    "ping",
    "profile",
    "psubscribe",
    "pttl",
    "publish",
    "pubsub_channels",
    "pubsub_numpat",
    "pubsub_numsub",
    "pubsub_shardchannels",
    "pubsub_shardnumsub",
    "punsubscribe",
    "quantile",
    "query",
    "queryindex",
    "quit",
    "randomkey",
    "range",
    "rank",
    "readonly",
    "readwrite",
    "rename",
    "replicaof",
    "reserve",
    "reset",
    "resp",
    "restore",
    "revrange",
    "revrank",
    "role",
    "rpoplpush",
    "rpush",
    "rpushx",
    "sadd",
    "save",
    "scan_iter",
    "scan",
    "scandump",
    "scard",
    "script_exists",
    "script_flush",
    "script_kill",
    "script_load",
    "sdiff",
    "sdiffstore",
    "search",
    "select",
    "set",
    "setbit",
    "setex",
    "setnx",
    "setrange",
    "sinter",
    "sintercard",
    "sinterstore",
    "sismember",
    "slaveof",
    "slowlog_get",
    "slowlog_len",
    "slowlog_reset",
    "slowlog",
    "smembers",
    "smismember",
    "smove",
    "spellcheck",
    "spublish",
    "srem",
    "sscan_iter",
    "sscan",
    "stralgo",
    "strappend",
    "strlen",
    "subscribe",
    "substr",
    "sugadd",
    "sugdel",
    "sugget",
    "suglen",
    "sunion",
    "sunionstore",
    "swapdb",
    "sync",
    "syndump",
    "synupdate",
    "tagvals",
    "tfcall_async",
    "tfcall",
    "tfunction_delete",
    "tfunction_list",
    "tfunction_load",
    "time",
    "toggle",
    "touch",
    "trimmed_mean",
    "ttl",
    "type",
    "unlink",
    "unsubscribe",
    "wait",
    "waitaof",
    "xack",
    "xadd",
    "xautoclaim",
    "xclaim",
    "xdel",
    "xgroup_create",
    "xgroup_createconsumer",
    "xgroup_del_consumer",
    "xgroup_delconsumer",
    "xgroup_destroy",
    "xgroup_set_id",
    "xgroup_setid",
    "xinfo_consumers",
    "xinfo_groups",
    "xinfo_help",
    "xinfo_stream",
    "xlen",
    "xpending_range",
    "xpending",
    "xrange",
    "xread_group",
    "xread",
    "xreadgroup",
    "xrevrange",
    "xtrim",
    "zadd",
    "zaddoption",
    "zcard",
    "zcount",
    "zdiff",
    "zdiffstore",
    "zincrby",
    "zinter",
    "zintercard",
    "zinterstore",
    "zmpop",
    "zmscore",
    "zpopmax",
    "zpopmin",
    "zrandmember",
    "zrange",
    "zrangebylex",
    "zrangebyscore",
    "zrangestore",
    "zrank",
    "zrem",
    "zremrangebylex",
    "zremrangebyrank",
    "zremrangebyscore",
    "zrevrange",
    "zrevrangebylex",
    "zrevrank",
    "zscan_iter",
    "zscan",
    "zscore",
    "zunion",
    "zunionstore",
}

_redis_client_gen_methods = {
    "scan_iter",
    "hscan_iter",
    "sscan_iter",
    "zscan_iter",
}

_redis_client_methods = _redis_client_sync_methods.union(_redis_client_async_methods)

_redis_multipart_commands = set(["client", "cluster", "command", "config", "debug", "sentinel", "slowlog", "script"])

_redis_operation_re = re.compile(r"[-\s]+")


def _conn_attrs_to_dict(connection):
    return {
        "host": getattr(connection, "host", None),
        "port": getattr(connection, "port", None),
        "path": getattr(connection, "path", None),
        "db": getattr(connection, "db", None),
    }


def _instance_info(kwargs):
    host = kwargs.get("host") or "localhost"
    port_path_or_id = str(kwargs.get("path") or kwargs.get("port", "unknown"))
    db = str(kwargs.get("db") or 0)

    return (host, port_path_or_id, db)


def _wrap_Redis_method_wrapper_(module, instance_class_name, operation):
    name = "%s.%s" % (instance_class_name, operation)
    if operation in _redis_client_gen_methods:
        async_wrapper = generator_wrapper
    else:
        async_wrapper = None

    wrap_datastore_trace(module, name, product="Redis", target=None, operation=operation, async_wrapper=async_wrapper)


def _wrap_asyncio_Redis_method_wrapper(module, instance_class_name, operation):
    def _nr_wrapper_asyncio_Redis_method_(wrapped, instance, args, kwargs):
        from redis.asyncio.client import Pipeline

        if isinstance(instance, Pipeline):
            return wrapped(*args, **kwargs)

        # Method should be run when awaited or iterated, therefore we wrap in an async wrapper.
        return DatastoreTraceWrapper(wrapped, product="Redis", target=None, operation=operation, async_wrapper=async_wrapper)(*args, **kwargs)

    name = "%s.%s" % (instance_class_name, operation)
    if operation in _redis_client_gen_methods:
        async_wrapper = async_generator_wrapper
    else:
        async_wrapper = coroutine_wrapper

    wrap_function_wrapper(module, name, _nr_wrapper_asyncio_Redis_method_)


async def wrap_async_Connection_send_command(wrapped, instance, args, kwargs):
    transaction = current_transaction()
    if not transaction:
        return await wrapped(*args, **kwargs)

    host, port_path_or_id, db = (None, None, None)

    try:
        dt = transaction.settings.datastore_tracer
        if dt.instance_reporting.enabled or dt.database_name_reporting.enabled:
            conn_kwargs = _conn_attrs_to_dict(instance)
            host, port_path_or_id, db = _instance_info(conn_kwargs)
    except Exception:
        pass

    # Older Redis clients would when sending multi part commands pass
    # them in as separate arguments to send_command(). Need to therefore
    # detect those and grab the next argument from the set of arguments.

    operation = args[0].strip().lower()

    # If it's not a multi part command, there's no need to trace it, so
    # we can return early.

    if (
        operation.split()[0] not in _redis_multipart_commands
    ):  # Set the datastore info on the DatastoreTrace containing this function call.
        trace = current_trace()

        # Find DatastoreTrace no matter how many other traces are inbetween
        while trace is not None and not isinstance(trace, DatastoreTrace):
            trace = getattr(trace, "parent", None)

        if trace is not None:
            trace.host = host
            trace.port_path_or_id = port_path_or_id
            trace.database_name = db

        return await wrapped(*args, **kwargs)

    # Convert multi args to single arg string

    if operation in _redis_multipart_commands and len(args) > 1:
        operation = "%s %s" % (operation, args[1].strip().lower())

    operation = _redis_operation_re.sub("_", operation)

    with DatastoreTrace(
        product="Redis", target=None, operation=operation, host=host, port_path_or_id=port_path_or_id, database_name=db
    ):
        return await wrapped(*args, **kwargs)


def _nr_Connection_send_command_wrapper_(wrapped, instance, args, kwargs):
    transaction = current_transaction()

    if transaction is None or not args:
        return wrapped(*args, **kwargs)

    host, port_path_or_id, db = (None, None, None)

    try:
        dt = transaction.settings.datastore_tracer
        if dt.instance_reporting.enabled or dt.database_name_reporting.enabled:
            conn_kwargs = _conn_attrs_to_dict(instance)
            host, port_path_or_id, db = _instance_info(conn_kwargs)
    except:
        pass

    # Find DatastoreTrace no matter how many other traces are inbetween
    trace = current_trace()
    while trace is not None and not isinstance(trace, DatastoreTrace):
        trace = getattr(trace, "parent", None)

    if trace is not None:
        trace.host = host
        trace.port_path_or_id = port_path_or_id
        trace.database_name = db

    # Older Redis clients would when sending multi part commands pass
    # them in as separate arguments to send_command(). Need to therefore
    # detect those and grab the next argument from the set of arguments.

    operation = args[0].strip().lower()

    # If it's not a multi part command, there's no need to trace it, so
    # we can return early.

    if operation.split()[0] not in _redis_multipart_commands:
        return wrapped(*args, **kwargs)

    # Convert multi args to single arg string

    if operation in _redis_multipart_commands and len(args) > 1:
        operation = "%s %s" % (operation, args[1].strip().lower())

    operation = _redis_operation_re.sub("_", operation)

    with DatastoreTrace(
        product="Redis",
        target=None,
        operation=operation,
        host=host,
        port_path_or_id=port_path_or_id,
        database_name=db,
        source=wrapped,
    ):
        return wrapped(*args, **kwargs)


def instrument_redis_client(module):
    if hasattr(module, "StrictRedis"):
        for name in _redis_client_methods:
            if name in vars(module.StrictRedis):
                _wrap_Redis_method_wrapper_(module, "StrictRedis", name)

    if hasattr(module, "Redis"):
        for name in _redis_client_methods:
            if name in vars(module.Redis):
                _wrap_Redis_method_wrapper_(module, "Redis", name)


def instrument_asyncio_redis_client(module):
    if hasattr(module, "Redis"):
        class_ = getattr(module, "Redis")
        for operation in _redis_client_async_methods:
            if hasattr(class_, operation):
                _wrap_asyncio_Redis_method_wrapper(module, "Redis", operation)

def instrument_redis_commands_core(module):
    _instrument_redis_commands_module(module, "CoreCommands")


def instrument_redis_commands_sentinel(module):
    _instrument_redis_commands_module(module, "SentinelCommands")


def instrument_redis_commands_json_commands(module):
    _instrument_redis_commands_module(module, "JSONCommands")


def instrument_redis_commands_search_commands(module):
    _instrument_redis_commands_module(module, "SearchCommands")


def instrument_redis_commands_timeseries_commands(module):
    _instrument_redis_commands_module(module, "TimeSeriesCommands")


def instrument_redis_commands_graph_commands(module):
    _instrument_redis_commands_module(module, "GraphCommands")


def instrument_redis_commands_bf_commands(module):
    _instrument_redis_commands_module(module, "BFCommands")
    _instrument_redis_commands_module(module, "CFCommands")
    _instrument_redis_commands_module(module, "CMSCommands")
    _instrument_redis_commands_module(module, "TDigestCommands")
    _instrument_redis_commands_module(module, "TOPKCommands")


def instrument_redis_commands_cluster(module):
    _instrument_redis_commands_module(module, "RedisClusterCommands")


def _instrument_redis_commands_module(module, class_name):
    for name in _redis_client_methods:
        if hasattr(module, class_name):
            class_instance = getattr(module, class_name)
            if hasattr(class_instance, name):
                _wrap_Redis_method_wrapper_(module, class_name, name)


def instrument_redis_connection(module):
    if hasattr(module, "Connection"):
        if hasattr(module.Connection, "send_command"):
            wrap_function_wrapper(module, "Connection.send_command", _nr_Connection_send_command_wrapper_)


def instrument_asyncio_redis_connection(module):
    if hasattr(module, "Connection"):
        if hasattr(module.Connection, "send_command"):
            wrap_function_wrapper(module, "Connection.send_command", wrap_async_Connection_send_command)
