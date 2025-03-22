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
This module implements functions for creating a unique identity from a name and set of tags for use in dimensional metrics.
"""

from newrelic.core.attribute import process_user_attribute


def create_metric_identity(name, tags=None):
    if tags:
        # Convert dicts to an iterable of tuples, other iterables should already be in this form
        if isinstance(tags, dict):
            tags = tags.items()  

        # Apply attribute system sanitization.
        # process_user_attribute returns (None, None) for results that fail sanitization.
        # The filter removes these results from the iterable before creating the frozenset.
        tags = frozenset(filter(lambda args: args[0] is not None, map(lambda args: process_user_attribute(*args), tags)))

    tags = tags or None  # Set empty iterables after filtering to None 

    return (name, tags)
