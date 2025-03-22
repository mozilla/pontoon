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

from typing import Any, Literal, cast

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
from .validate import MF2ValidationError


def mf2_from_json(json: dict[str, Any]) -> Message:
    """
    Marshal a MessageFormat 2 data model [JSON Schema](https://github.com/unicode-org/message-format-wg/blob/main/spec/data-model/message.json)
    object into a parsed `moz.l10n.message.data.Message`.

    May raise `MF2ValidationError`.
    """
    try:
        msg_type = json["type"]
        if msg_type not in {"message", "select"}:
            raise MF2ValidationError(f"Invalid JSON message: {json}")

        declarations: dict[str, Expression] = {}
        for decl in json["declarations"]:
            decl_type = decl["type"]
            if decl_type not in {"input", "local"}:
                raise MF2ValidationError(f"Invalid JSON declaration type: {decl}")
            decl_name = _string(decl, "name")
            decl_expr = _expression(decl["value"])
            if decl_type == "input":
                if (
                    not isinstance(decl_expr.arg, VariableRef)
                    or decl_expr.arg.name != decl_name
                ):
                    raise MF2ValidationError(f"Invalid JSON .input declaration: {decl}")
            if decl_name in declarations:
                raise MF2ValidationError(f"Duplicate JSON declaration for ${decl_name}")
            declarations[decl_name] = decl_expr

        if msg_type == "message":
            pattern = _pattern(json["pattern"])
            return PatternMessage(pattern, declarations)

        assert msg_type == "select"
        selectors = tuple(_variable(sel) for sel in json["selectors"])
        variants = {
            tuple(_key(key) for key in vari["keys"]): _pattern(vari["value"])
            for vari in json["variants"]
        }
        return SelectMessage(declarations, selectors, variants)
    except (IndexError, KeyError, TypeError) as err:
        raise MF2ValidationError(f"Invalid JSON: {err!r}")


def _pattern(json: list[Any]) -> Pattern:
    return [
        part
        if isinstance(part, str)
        else _markup(part)
        if part["type"] == "markup"
        else _expression(part)
        for part in json
    ]


def _expression(json: dict[str, Any]) -> Expression:
    if json["type"] != "expression":
        raise MF2ValidationError(f"Invalid JSON expression type: {json}")
    arg = _value(json["arg"]) if "arg" in json else None
    json_func = json.get("function", None)
    if json_func:
        if json_func["type"] != "function":
            raise MF2ValidationError(f"Invalid JSON function type: {json_func}")
        function = _string(json_func, "name")
        options = _options(json_func["options"]) if "options" in json_func else {}
    else:
        function = None
        options = {}
    if arg is None and function is None:
        raise MF2ValidationError(
            f"Invalid JSON expression with no operand and no function: {json}"
        )
    attributes = _attributes(json["attributes"]) if "attributes" in json else {}
    return Expression(arg, function, options, attributes)


def _markup(json: dict[str, Any]) -> Markup:
    assert json["type"] == "markup"
    kind = cast(Literal["open", "standalone", "close"], _string(json, "kind"))
    if kind not in {"open", "standalone", "close"}:
        raise MF2ValidationError(f"Invalid JSON markup kind: {json}")
    name = _string(json, "name")
    options = _options(json["options"]) if "options" in json else {}
    attributes = _attributes(json["attributes"]) if "attributes" in json else {}
    return Markup(kind, name, options, attributes)


def _options(json: dict[str, Any]) -> dict[str, str | VariableRef]:
    return {name: _value(json_value) for name, json_value in json.items()}


def _attributes(json: dict[str, Any]) -> dict[str, str | Literal[True]]:
    return {
        name: True if json_value is True else _literal(json_value)
        for name, json_value in json.items()
    }


def _key(json: dict[str, Any]) -> str | CatchallKey:
    type = json["type"]
    if type == "literal":
        return _string(json, "value")
    elif json["type"] == "*":
        value = _string(json, "value") if "value" in json else None
        return CatchallKey(value)
    else:
        raise MF2ValidationError(f"Invalid JSON variant key: {json}")


def _value(json: dict[str, Any]) -> str | VariableRef:
    return _string(json, "value") if json["type"] == "literal" else _variable(json)


def _literal(json: dict[str, Any]) -> str:
    if json["type"] != "literal":
        raise MF2ValidationError(f"Invalid JSON literal: {json}")
    return _string(json, "value")


def _variable(json: dict[str, Any]) -> VariableRef:
    if json["type"] != "variable":
        raise MF2ValidationError(f"Invalid JSON variable: {json}")
    return VariableRef(_string(json, "name"))


def _string(obj: dict[str, Any], key: str | None = None) -> str:
    value = obj if key is None else obj.get(key, None)
    if isinstance(value, str):
        return value
    else:
        raise MF2ValidationError(f"Expected a string value for {key} in {obj}")
