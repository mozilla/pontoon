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

from newrelic.packages import six

if six.PY3:
    from inspect import Signature

    def bind_args(func, args, kwargs):
        """Bind arguments and apply defaults to missing arguments for a callable."""
        bound_args = Signature.from_callable(func).bind(*args, **kwargs)
        bound_args.apply_defaults()
        return bound_args.arguments

else:
    from inspect import getcallargs

    def bind_args(func, args, kwargs):
        """Bind arguments and apply defaults to missing arguments for a callable."""
        return getcallargs(func, *args, **kwargs)
