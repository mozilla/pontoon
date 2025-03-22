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

from typing import Any, Literal

from ...model import (
    CatchallKey,
    Expression,
    Markup,
    Message,
    Pattern,
    PatternMessage,
    SelectMessage,
    VariableRef,
)


def mf2_to_json(message: Message) -> dict[str, Any]:
    """
    Represent a message using the MessageFormat 2 data model [JSON Schema](https://github.com/unicode-org/message-format-wg/blob/main/spec/data-model/message.json).

    Does not validate the message; for that, use `mf2_validate_message()`.
    """
    json_declarations = [
        {
            "type": (
                "input"
                if isinstance(expr.arg, VariableRef) and expr.arg.name == name
                else "local"
            ),
            "name": name,
            "value": _expression(expr),
        }
        for name, expr in message.declarations.items()
    ]

    if isinstance(message, PatternMessage):
        return {
            "type": "message",
            "declarations": json_declarations,
            "pattern": _pattern(message.pattern),
        }
    else:
        assert isinstance(message, SelectMessage)
        return {
            "type": "select",
            "declarations": json_declarations,
            "selectors": [_variable(sel) for sel in message.selectors],
            "variants": [
                {"keys": [_key(key) for key in keys], "value": _pattern(pattern)}
                for keys, pattern in message.variants.items()
            ],
        }


def _pattern(pattern: Pattern) -> list[Any]:
    return [
        part
        if isinstance(part, str)
        else _markup(part)
        if isinstance(part, Markup)
        else _expression(part)
        for part in pattern
    ]


def _expression(expr: Expression) -> dict[str, str | dict[str, Any]]:
    json: dict[str, Any] = {"type": "expression"}
    if expr.arg is not None:
        json["arg"] = _value(expr.arg)
    if expr.function is not None:
        json_func: dict[str, Any] = {"type": "function", "name": expr.function}
        if expr.options:
            json_func["options"] = _options(expr.options)
        json["function"] = json_func
    if expr.attributes:
        json["attributes"] = _attributes(expr.attributes)
    return json


def _markup(markup: Markup) -> dict[str, str | dict[str, Any]]:
    json: dict[str, Any] = {
        "type": "markup",
        "kind": markup.kind,
        "name": markup.name,
    }
    if markup.options:
        json["options"] = _options(markup.options)
    if markup.attributes:
        json["attributes"] = _attributes(markup.attributes)
    return json


def _options(
    options: dict[str, str | VariableRef],
) -> dict[str, dict[str, str]]:
    return {name: _value(value) for name, value in options.items()}


def _attributes(
    attributes: dict[str, str | Literal[True]],
) -> dict[str, dict[str, str] | Literal[True]]:
    return {
        name: True if value is True else _literal(value)
        for name, value in attributes.items()
    }


def _key(key: str | CatchallKey) -> str | dict[str, str]:
    if isinstance(key, str):
        return _literal(key)
    else:
        json = {"type": "*"}
        if key.value is not None:
            json["value"] = key.value
        return json


def _value(value: str | VariableRef) -> dict[str, str]:
    return _literal(value) if isinstance(value, str) else _variable(value)


def _literal(value: str) -> dict[str, str]:
    return {"type": "literal", "value": value}


def _variable(var: VariableRef) -> dict[str, str]:
    return {"type": "variable", "name": var.name}
