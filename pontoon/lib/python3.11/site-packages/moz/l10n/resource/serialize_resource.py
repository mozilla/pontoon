# Copyright Mozilla Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from collections.abc import Iterator
from typing import Callable

from ..formats import Format
from ..formats.dtd.serialize import dtd_serialize
from ..formats.fluent.serialize import fluent_serialize
from ..formats.inc.serialize import inc_serialize
from ..formats.ini.serialize import ini_serialize
from ..formats.plain_json.serialize import plain_json_serialize
from ..formats.po.serialize import po_serialize
from ..formats.properties.serialize import properties_serialize
from ..formats.webext.serialize import webext_serialize
from ..model import Message, Resource

android_serialize: (
    Callable[[Resource[str] | Resource[Message], bool], Iterator[str]] | None
)
xliff_serialize: (
    Callable[[Resource[str] | Resource[Message], bool], Iterator[str]] | None
)
try:
    from ..formats.android.serialize import android_serialize
    from ..formats.xliff.serialize import xliff_serialize
except ImportError:
    android_serialize = None
    xliff_serialize = None


def serialize_resource(
    resource: Resource[str] | Resource[Message],
    format: Format | None = None,
    trim_comments: bool = False,
) -> Iterator[str]:
    """
    Serialize a Resource as its string representation.

    If `format` is set, it overrides the `resource.format` value.

    With `trim_comments`,
    all standalone and attached comments are left out of the serialization.
    """
    # TODO post-py38: should be a match
    if not format:
        format = resource.format
    if format == Format.dtd:
        return dtd_serialize(resource, trim_comments=trim_comments)
    elif format == Format.fluent:
        return fluent_serialize(resource, trim_comments=trim_comments)
    elif format == Format.inc:
        return inc_serialize(resource, trim_comments=trim_comments)
    elif format == Format.ini:
        return ini_serialize(resource, trim_comments=trim_comments)
    elif format == Format.plain_json:
        return plain_json_serialize(resource, trim_comments=trim_comments)
    elif format == Format.po:
        return po_serialize(resource, trim_comments=trim_comments)
    elif format == Format.properties:
        return properties_serialize(resource, trim_comments=trim_comments)
    elif format == Format.webext:
        return webext_serialize(resource, trim_comments=trim_comments)
    elif format == Format.android and android_serialize is not None:
        return android_serialize(resource, trim_comments)
    elif format == Format.xliff and xliff_serialize is not None:
        return xliff_serialize(resource, trim_comments)
    else:
        raise ValueError(f"Unsupported resource format: {format or resource.format}")
