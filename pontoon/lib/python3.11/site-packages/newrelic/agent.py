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

from newrelic.api.application import application_instance as __application
from newrelic.api.application import application_settings as __application_settings
from newrelic.api.application import register_application as __register_application
from newrelic.api.log import NewRelicContextFormatter as __NewRelicContextFormatter
from newrelic.api.time_trace import (
    add_custom_span_attribute as __add_custom_span_attribute,
)
from newrelic.api.time_trace import current_trace as __current_trace
from newrelic.api.time_trace import get_linking_metadata as __get_linking_metadata
from newrelic.api.time_trace import notice_error as __notice_error
from newrelic.api.time_trace import record_exception as __record_exception
from newrelic.api.transaction import (
    accept_distributed_trace_headers as __accept_distributed_trace_headers,
)
from newrelic.api.transaction import (
    accept_distributed_trace_payload as __accept_distributed_trace_payload,
)
from newrelic.api.transaction import add_custom_attribute as __add_custom_attribute
from newrelic.api.transaction import add_custom_attributes as __add_custom_attributes
from newrelic.api.transaction import add_custom_parameter as __add_custom_parameter
from newrelic.api.transaction import add_custom_parameters as __add_custom_parameters
from newrelic.api.transaction import add_framework_info as __add_framework_info
from newrelic.api.transaction import capture_request_params as __capture_request_params
from newrelic.api.transaction import (
    create_distributed_trace_payload as __create_distributed_trace_payload,
)
from newrelic.api.transaction import current_span_id as __current_span_id
from newrelic.api.transaction import current_trace_id as __current_trace_id
from newrelic.api.transaction import current_transaction as __current_transaction
from newrelic.api.transaction import (
    disable_browser_autorum as __disable_browser_autorum,
)
from newrelic.api.transaction import end_of_transaction as __end_of_transaction
from newrelic.api.transaction import (
    get_browser_timing_footer as __get_browser_timing_footer,
)
from newrelic.api.transaction import (
    get_browser_timing_header as __get_browser_timing_header,
)
from newrelic.api.transaction import ignore_transaction as __ignore_transaction
from newrelic.api.transaction import (
    insert_distributed_trace_headers as __insert_distributed_trace_headers,
)
from newrelic.api.transaction import record_custom_event as __record_custom_event
from newrelic.api.transaction import record_custom_metric as __record_custom_metric
from newrelic.api.transaction import record_custom_metrics as __record_custom_metrics
from newrelic.api.transaction import record_log_event as __record_log_event
from newrelic.api.transaction import record_ml_event as __record_ml_event
from newrelic.api.transaction import set_background_task as __set_background_task
from newrelic.api.transaction import set_transaction_name as __set_transaction_name
from newrelic.api.transaction import suppress_apdex_metric as __suppress_apdex_metric
from newrelic.api.transaction import (
    suppress_transaction_trace as __suppress_transaction_trace,
)
from newrelic.api.wsgi_application import (
    WSGIApplicationWrapper as __WSGIApplicationWrapper,
)
from newrelic.api.wsgi_application import (
    wrap_wsgi_application as __wrap_wsgi_application,
)
from newrelic.api.wsgi_application import wsgi_application as __wsgi_application
from newrelic.config import extra_settings as __extra_settings
from newrelic.config import initialize as __initialize
from newrelic.core.agent import register_data_source as __register_data_source
from newrelic.core.agent import shutdown_agent as __shutdown_agent
from newrelic.core.config import global_settings as __global_settings
from newrelic.samplers.decorators import data_source_factory as __data_source_factory
from newrelic.samplers.decorators import (
    data_source_generator as __data_source_generator,
)

try:
    from newrelic.api.asgi_application import (
        ASGIApplicationWrapper as __ASGIApplicationWrapper,
    )
    from newrelic.api.asgi_application import asgi_application as __asgi_application
    from newrelic.api.asgi_application import (
        wrap_asgi_application as __wrap_asgi_application,
    )
except SyntaxError:

    def __asgi_application(*args, **kwargs):
        pass

    __ASGIApplicationWrapper = __asgi_application
    __wrap_asgi_application = __asgi_application

from newrelic.api.background_task import BackgroundTask as __BackgroundTask
from newrelic.api.background_task import (
    BackgroundTaskWrapper as __BackgroundTaskWrapper,
)
from newrelic.api.background_task import background_task as __background_task
from newrelic.api.background_task import wrap_background_task as __wrap_background_task
from newrelic.api.database_trace import DatabaseTrace as __DatabaseTrace
from newrelic.api.database_trace import DatabaseTraceWrapper as __DatabaseTraceWrapper
from newrelic.api.database_trace import database_trace as __database_trace
from newrelic.api.database_trace import (
    register_database_client as __register_database_client,
)
from newrelic.api.database_trace import wrap_database_trace as __wrap_database_trace
from newrelic.api.datastore_trace import DatastoreTrace as __DatastoreTrace
from newrelic.api.datastore_trace import (
    DatastoreTraceWrapper as __DatastoreTraceWrapper,
)
from newrelic.api.datastore_trace import datastore_trace as __datastore_trace
from newrelic.api.datastore_trace import wrap_datastore_trace as __wrap_datastore_trace
from newrelic.api.error_trace import ErrorTrace as __ErrorTrace
from newrelic.api.error_trace import ErrorTraceWrapper as __ErrorTraceWrapper
from newrelic.api.error_trace import error_trace as __error_trace
from newrelic.api.error_trace import wrap_error_trace as __wrap_error_trace
from newrelic.api.external_trace import ExternalTrace as __ExternalTrace
from newrelic.api.external_trace import ExternalTraceWrapper as __ExternalTraceWrapper
from newrelic.api.external_trace import external_trace as __external_trace
from newrelic.api.external_trace import wrap_external_trace as __wrap_external_trace
from newrelic.api.function_trace import FunctionTrace as __FunctionTrace
from newrelic.api.function_trace import FunctionTraceWrapper as __FunctionTraceWrapper
from newrelic.api.function_trace import function_trace as __function_trace
from newrelic.api.function_trace import wrap_function_trace as __wrap_function_trace
from newrelic.api.generator_trace import (
    GeneratorTraceWrapper as __GeneratorTraceWrapper,
)
from newrelic.api.generator_trace import generator_trace as __generator_trace
from newrelic.api.generator_trace import wrap_generator_trace as __wrap_generator_trace
from newrelic.api.html_insertion import insert_html_snippet as __insert_html_snippet
from newrelic.api.html_insertion import verify_body_exists as __verify_body_exists
from newrelic.api.lambda_handler import LambdaHandlerWrapper as __LambdaHandlerWrapper
from newrelic.api.lambda_handler import lambda_handler as __lambda_handler
from newrelic.api.message_trace import MessageTrace as __MessageTrace
from newrelic.api.message_trace import MessageTraceWrapper as __MessageTraceWrapper
from newrelic.api.message_trace import message_trace as __message_trace
from newrelic.api.message_trace import wrap_message_trace as __wrap_message_trace
from newrelic.api.message_transaction import MessageTransaction as __MessageTransaction
from newrelic.api.message_transaction import (
    MessageTransactionWrapper as __MessageTransactionWrapper,
)
from newrelic.api.message_transaction import (
    message_transaction as __message_transaction,
)
from newrelic.api.message_transaction import (
    wrap_message_transaction as __wrap_message_transaction,
)
from newrelic.api.ml_model import wrap_mlmodel as __wrap_mlmodel
from newrelic.api.profile_trace import ProfileTraceWrapper as __ProfileTraceWrapper
from newrelic.api.profile_trace import profile_trace as __profile_trace
from newrelic.api.profile_trace import wrap_profile_trace as __wrap_profile_trace
from newrelic.api.settings import set_error_group_callback as __set_error_group_callback
from newrelic.api.supportability import wrap_api_call as __wrap_api_call
from newrelic.api.transaction import set_user_id as __set_user_id
from newrelic.api.transaction_name import (
    TransactionNameWrapper as __TransactionNameWrapper,
)
from newrelic.api.transaction_name import transaction_name as __transaction_name
from newrelic.api.transaction_name import (
    wrap_transaction_name as __wrap_transaction_name,
)
from newrelic.api.web_transaction import WebTransaction as __WebTransaction
from newrelic.api.web_transaction import (
    WebTransactionWrapper as __WebTransactionWrapper,
)
from newrelic.api.web_transaction import web_transaction as __web_transaction
from newrelic.api.web_transaction import wrap_web_transaction as __wrap_web_transaction
from newrelic.common.object_names import callable_name as __callable_name
from newrelic.common.object_wrapper import FunctionWrapper as __FunctionWrapper
from newrelic.common.object_wrapper import InFunctionWrapper as __InFunctionWrapper
from newrelic.common.object_wrapper import ObjectProxy as __ObjectProxy
from newrelic.common.object_wrapper import CallableObjectProxy as __CallableObjectProxy
from newrelic.common.object_wrapper import ObjectWrapper as __ObjectWrapper
from newrelic.common.object_wrapper import OutFunctionWrapper as __OutFunctionWrapper
from newrelic.common.object_wrapper import PostFunctionWrapper as __PostFunctionWrapper
from newrelic.common.object_wrapper import PreFunctionWrapper as __PreFunctionWrapper
from newrelic.common.object_wrapper import function_wrapper as __function_wrapper
from newrelic.common.object_wrapper import in_function as __in_function
from newrelic.common.object_wrapper import out_function as __out_function
from newrelic.common.object_wrapper import (
    patch_function_wrapper as __patch_function_wrapper,
)
from newrelic.common.object_wrapper import post_function as __post_function
from newrelic.common.object_wrapper import pre_function as __pre_function
from newrelic.common.object_wrapper import resolve_path as __resolve_path
from newrelic.common.object_wrapper import (
    transient_function_wrapper as __transient_function_wrapper,
)
from newrelic.common.object_wrapper import (
    wrap_function_wrapper as __wrap_function_wrapper,
)
from newrelic.common.object_wrapper import wrap_in_function as __wrap_in_function
from newrelic.common.object_wrapper import wrap_object as __wrap_object
from newrelic.common.object_wrapper import (
    wrap_object_attribute as __wrap_object_attribute,
)
from newrelic.common.object_wrapper import wrap_out_function as __wrap_out_function
from newrelic.common.object_wrapper import wrap_post_function as __wrap_post_function
from newrelic.common.object_wrapper import wrap_pre_function as __wrap_pre_function

# EXPERIMENTAL - Generator traces are currently experimental and may not
# exist in this form in future versions of the agent.

initialize = __initialize
extra_settings = __wrap_api_call(__extra_settings, "extra_settings")
global_settings = __wrap_api_call(__global_settings, "global_settings")
shutdown_agent = __wrap_api_call(__shutdown_agent, "shutdown_agent")
register_data_source = __wrap_api_call(__register_data_source, "register_data_source")
data_source_generator = __wrap_api_call(__data_source_generator, "data_source_generator")
data_source_factory = __wrap_api_call(__data_source_factory, "data_source_factory")
application = __wrap_api_call(__application, "application")
register_application = __register_application
application_settings = __wrap_api_call(__application_settings, "application_settings")
current_trace = __wrap_api_call(__current_trace, "current_trace")
get_linking_metadata = __wrap_api_call(__get_linking_metadata, "get_linking_metadata")
add_custom_span_attribute = __wrap_api_call(__add_custom_span_attribute, "add_custom_span_attribute")
current_transaction = __wrap_api_call(__current_transaction, "current_transaction")
set_user_id = __wrap_api_call(__set_user_id, "set_user_id")
set_error_group_callback = __wrap_api_call(__set_error_group_callback, "set_error_group_callback")
set_transaction_name = __wrap_api_call(__set_transaction_name, "set_transaction_name")
end_of_transaction = __wrap_api_call(__end_of_transaction, "end_of_transaction")
set_background_task = __wrap_api_call(__set_background_task, "set_background_task")
ignore_transaction = __wrap_api_call(__ignore_transaction, "ignore_transaction")
suppress_apdex_metric = __wrap_api_call(__suppress_apdex_metric, "suppress_apdex_metric")
capture_request_params = __wrap_api_call(__capture_request_params, "capture_request_params")
add_custom_parameter = __wrap_api_call(__add_custom_parameter, "add_custom_parameter")
add_custom_parameters = __wrap_api_call(__add_custom_parameters, "add_custom_parameters")
add_custom_attribute = __wrap_api_call(__add_custom_attribute, "add_custom_attribute")
add_custom_attributes = __wrap_api_call(__add_custom_attributes, "add_custom_attributes")
add_framework_info = __wrap_api_call(__add_framework_info, "add_framework_info")
record_exception = __wrap_api_call(__record_exception, "record_exception")
notice_error = __wrap_api_call(__notice_error, "notice_error")
get_browser_timing_header = __wrap_api_call(__get_browser_timing_header, "get_browser_timing_header")
get_browser_timing_footer = __wrap_api_call(__get_browser_timing_footer, "get_browser_timing_footer")
disable_browser_autorum = __wrap_api_call(__disable_browser_autorum, "disable_browser_autorum")
suppress_transaction_trace = __wrap_api_call(__suppress_transaction_trace, "suppress_transaction_trace")
record_custom_metric = __wrap_api_call(__record_custom_metric, "record_custom_metric")
record_custom_metrics = __wrap_api_call(__record_custom_metrics, "record_custom_metrics")
record_custom_event = __wrap_api_call(__record_custom_event, "record_custom_event")
record_log_event = __wrap_api_call(__record_log_event, "record_log_event")
record_ml_event = __wrap_api_call(__record_ml_event, "record_ml_event")
accept_distributed_trace_payload = __wrap_api_call(
    __accept_distributed_trace_payload, "accept_distributed_trace_payload"
)
create_distributed_trace_payload = __wrap_api_call(
    __create_distributed_trace_payload, "create_distributed_trace_payload"
)
accept_distributed_trace_headers = __wrap_api_call(
    __accept_distributed_trace_headers, "accept_distributed_trace_headers"
)
insert_distributed_trace_headers = __wrap_api_call(
    __insert_distributed_trace_headers, "insert_distributed_trace_headers"
)
current_trace_id = __wrap_api_call(__current_trace_id, "current_trace_id")
current_span_id = __wrap_api_call(__current_span_id, "current_span_id")
wsgi_application = __wsgi_application
asgi_application = __asgi_application
WebTransaction = __wrap_api_call(__WebTransaction, "WebTransaction")
web_transaction = __wrap_api_call(__web_transaction, "web_transaction")
WebTransactionWrapper = __wrap_api_call(__WebTransactionWrapper, "WebTransactionWrapper")
wrap_web_transaction = __wrap_api_call(__wrap_web_transaction, "wrap_web_transaction")
WSGIApplicationWrapper = __WSGIApplicationWrapper
wrap_wsgi_application = __wrap_wsgi_application
ASGIApplicationWrapper = __ASGIApplicationWrapper
wrap_asgi_application = __wrap_asgi_application
background_task = __wrap_api_call(__background_task, "background_task")
BackgroundTask = __wrap_api_call(__BackgroundTask, "BackgroundTask")
BackgroundTaskWrapper = __wrap_api_call(__BackgroundTaskWrapper, "BackgroundTaskWrapper")
wrap_background_task = __wrap_api_call(__wrap_background_task, "wrap_background_task")
LambdaHandlerWrapper = __wrap_api_call(__LambdaHandlerWrapper, "LambdaHandlerWrapper")
lambda_handler = __wrap_api_call(__lambda_handler, "lambda_handler")
NewRelicContextFormatter = __wrap_api_call(__NewRelicContextFormatter, "NewRelicContextFormatter")
transaction_name = __wrap_api_call(__transaction_name, "transaction_name")
TransactionNameWrapper = __wrap_api_call(__TransactionNameWrapper, "TransactionNameWrapper")
wrap_transaction_name = __wrap_api_call(__wrap_transaction_name, "wrap_transaction_name")
function_trace = __wrap_api_call(__function_trace, "function_trace")
FunctionTrace = __wrap_api_call(__FunctionTrace, "FunctionTrace")
FunctionTraceWrapper = __wrap_api_call(__FunctionTraceWrapper, "FunctionTraceWrapper")
wrap_function_trace = __wrap_api_call(__wrap_function_trace, "wrap_function_trace")
generator_trace = __wrap_api_call(__generator_trace, "generator_trace")
GeneratorTraceWrapper = __wrap_api_call(__GeneratorTraceWrapper, "GeneratorTraceWrapper")
wrap_generator_trace = __wrap_api_call(__wrap_generator_trace, "wrap_generator_trace")
profile_trace = __wrap_api_call(__profile_trace, "profile_trace")
ProfileTraceWrapper = __wrap_api_call(__ProfileTraceWrapper, "ProfileTraceWrapper")
wrap_profile_trace = __wrap_api_call(__wrap_profile_trace, "wrap_profile_trace")
database_trace = __wrap_api_call(__database_trace, "database_trace")
DatabaseTrace = __wrap_api_call(__DatabaseTrace, "DatabaseTrace")
DatabaseTraceWrapper = __wrap_api_call(__DatabaseTraceWrapper, "DatabaseTraceWrapper")
wrap_database_trace = __wrap_api_call(__wrap_database_trace, "wrap_database_trace")
register_database_client = __wrap_api_call(__register_database_client, "register_database_client")
datastore_trace = __wrap_api_call(__datastore_trace, "datastore_trace")
DatastoreTrace = __wrap_api_call(__DatastoreTrace, "DatastoreTrace")
DatastoreTraceWrapper = __wrap_api_call(__DatastoreTraceWrapper, "DatastoreTraceWrapper")
wrap_datastore_trace = __wrap_api_call(__wrap_datastore_trace, "wrap_datastore_trace")
external_trace = __wrap_api_call(__external_trace, "external_trace")
ExternalTrace = __wrap_api_call(__ExternalTrace, "ExternalTrace")
ExternalTraceWrapper = __wrap_api_call(__ExternalTraceWrapper, "ExternalTraceWrapper")
wrap_external_trace = __wrap_api_call(__wrap_external_trace, "wrap_external_trace")
error_trace = __wrap_api_call(__error_trace, "error_trace")
ErrorTrace = __wrap_api_call(__ErrorTrace, "ErrorTrace")
ErrorTraceWrapper = __wrap_api_call(__ErrorTraceWrapper, "ErrorTraceWrapper")
wrap_error_trace = __wrap_api_call(__wrap_error_trace, "wrap_error_trace")
message_trace = __wrap_api_call(__message_trace, "message_trace")
MessageTrace = __wrap_api_call(__MessageTrace, "MessageTrace")
MessageTraceWrapper = __wrap_api_call(__MessageTraceWrapper, "MessageTraceWrapper")
wrap_message_trace = __wrap_api_call(__wrap_message_trace, "wrap_message_trace")
message_transaction = __wrap_api_call(__message_transaction, "message_trace")
MessageTransaction = __wrap_api_call(__MessageTransaction, "MessageTransaction")
MessageTransactionWrapper = __wrap_api_call(__MessageTransactionWrapper, "MessageTransactionWrapper")
wrap_message_transaction = __wrap_api_call(__wrap_message_transaction, "wrap_message_transaction")
callable_name = __wrap_api_call(__callable_name, "callable_name")
ObjectProxy = __wrap_api_call(__ObjectProxy, "ObjectProxy")
CallableObjectProxy = __wrap_api_call(__CallableObjectProxy, "CallableObjectProxy")
wrap_object = __wrap_api_call(__wrap_object, "wrap_object")
wrap_object_attribute = __wrap_api_call(__wrap_object_attribute, "wrap_object_attribute")
resolve_path = __wrap_api_call(__resolve_path, "resolve_path")
transient_function_wrapper = __wrap_api_call(__transient_function_wrapper, "transient_function_wrapper")
FunctionWrapper = __wrap_api_call(__FunctionWrapper, "FunctionWrapper")
function_wrapper = __wrap_api_call(__function_wrapper, "function_wrapper")
wrap_function_wrapper = __wrap_api_call(__wrap_function_wrapper, "wrap_function_wrapper")
patch_function_wrapper = __wrap_api_call(__patch_function_wrapper, "patch_function_wrapper")
ObjectWrapper = __wrap_api_call(__ObjectWrapper, "ObjectWrapper")
pre_function = __wrap_api_call(__pre_function, "pre_function")
PreFunctionWrapper = __wrap_api_call(__PreFunctionWrapper, "PreFunctionWrapper")
wrap_pre_function = __wrap_api_call(__wrap_pre_function, "wrap_pre_function")
post_function = __wrap_api_call(__post_function, "post_function")
PostFunctionWrapper = __wrap_api_call(__PostFunctionWrapper, "PostFunctionWrapper")
wrap_post_function = __wrap_api_call(__wrap_post_function, "wrap_post_function")
in_function = __wrap_api_call(__in_function, "in_function")
InFunctionWrapper = __wrap_api_call(__InFunctionWrapper, "InFunctionWrapper")
wrap_in_function = __wrap_api_call(__wrap_in_function, "wrap_in_function")
out_function = __wrap_api_call(__out_function, "out_function")
OutFunctionWrapper = __wrap_api_call(__OutFunctionWrapper, "OutFunctionWrapper")
wrap_out_function = __wrap_api_call(__wrap_out_function, "wrap_out_function")
insert_html_snippet = __wrap_api_call(__insert_html_snippet, "insert_html_snippet")
verify_body_exists = __wrap_api_call(__verify_body_exists, "verify_body_exists")
wrap_mlmodel = __wrap_api_call(__wrap_mlmodel, "wrap_mlmodel")
