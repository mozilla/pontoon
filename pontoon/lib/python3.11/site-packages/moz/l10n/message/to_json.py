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

from typing import Any

from ..model import (
    Expression,
    Markup,
    Message,
    Pattern,
    PatternMessage,
    SelectMessage,
    VariableRef,
)


def message_to_json(msg: Message) -> list[Any] | dict[str, Any]:
    """
    Represent a Message as a JSON-serializable value.

    The JSON Schema of the output is provided as [schema.json](./schema.json).
    """
    json_declarations = {
        name: _expression_to_json(expr) for name, expr in msg.declarations.items()
    }
    if isinstance(msg, PatternMessage):
        if not json_declarations:
            return _pattern_to_json(msg.pattern)
        return {
            "decl": json_declarations,
            "msg": _pattern_to_json(msg.pattern),
        }
    else:
        assert isinstance(msg, SelectMessage)
        return {
            "decl": json_declarations,
            "sel": [sel.name for sel in msg.selectors],
            "alt": [
                {
                    "keys": [
                        key if isinstance(key, str) else {"*": key.value or ""}
                        for key in keys
                    ],
                    "pat": _pattern_to_json(pattern),
                }
                for keys, pattern in msg.variants.items()
            ],
        }


def _pattern_to_json(pattern: Pattern) -> list[str | dict[str, Any]]:
    return [
        part
        if isinstance(part, str)
        else _markup_to_json(part)
        if isinstance(part, Markup)
        else _expression_to_json(part)
        for part in pattern
    ]


def _expression_to_json(expr: Expression) -> dict[str, Any]:
    json: dict[str, Any] = {}
    if isinstance(expr.arg, str):
        json["_"] = expr.arg
    elif isinstance(expr.arg, VariableRef):
        json["$"] = expr.arg.name
    if expr.function:
        json["fn"] = expr.function
        if expr.options:
            json["opt"] = _options_to_json(expr.options)
    if expr.attributes:
        json["attr"] = expr.attributes
    return json


def _markup_to_json(markup: Markup) -> dict[str, Any]:
    json: dict[str, Any] = {
        "elem" if markup.kind == "standalone" else markup.kind: markup.name
    }
    if markup.options:
        json["opt"] = _options_to_json(markup.options)
    if markup.attributes:
        json["attr"] = markup.attributes
    return json


def _options_to_json(options: dict[str, str | VariableRef]) -> dict[str, Any]:
    return {
        name: value if isinstance(value, str) else {"$": value.name}
        for name, value in options.items()
    }
