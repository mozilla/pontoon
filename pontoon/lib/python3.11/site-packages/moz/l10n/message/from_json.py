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

from collections.abc import Mapping
from typing import Any, Literal

from ..model import (
    CatchallKey,
    Expression,
    Markup,
    Message,
    Pattern,
    PatternMessage,
    SelectMessage,
    VariableRef,
)


def message_from_json(json: list[Any] | dict[str, Any]) -> Message:
    """
    Marshal the JSON output of `moz.l10n.message.to_json()`
    back into a parsed `moz.l10n.message.data.Message`.

    May raise `MF2ValidationError`.
    """
    if isinstance(json, Mapping) and "sel" in json:
        return SelectMessage(
            declarations={
                name: _expression_from_json(value)
                for name, value in json["decl"].items()
            },
            selectors=tuple(VariableRef(sel) for sel in json["sel"]),
            variants={
                tuple(
                    key if isinstance(key, str) else CatchallKey(key["*"] or None)
                    for key in variant["keys"]
                ): _pattern_from_json(variant["pat"])
                for variant in json["alt"]
            },
        )
    else:
        declarations = {}
        if isinstance(json, Mapping):
            if "decl" in json:
                declarations = {
                    name: _expression_from_json(value)
                    for name, value in json["decl"].items()
                }
            pattern = _pattern_from_json(json["msg"])
        else:
            pattern = _pattern_from_json(json)
        return PatternMessage(pattern, declarations)


def _pattern_from_json(json: list[str | dict[str, Any]]) -> Pattern:
    return [
        part
        if isinstance(part, str)
        else _expression_from_json(part)
        if "_" in part or "$" in part or "fn" in part
        else _markup_from_json(part)
        for part in json
    ]


def _expression_from_json(json: dict[str, Any]) -> Expression:
    if "_" in json:
        arg = json["_"]
    elif "$" in json:
        arg = VariableRef(json["$"])
    else:
        arg = None
    function = json.get("fn", None)
    options = (
        _options_from_json(json["opt"])
        if function is not None and "opt" in json
        else {}
    )
    return Expression(arg, function, options, json.get("attr", {}))


def _markup_from_json(json: dict[str, Any]) -> Markup:
    kind: Literal["open", "standalone", "close"]
    if "open" in json:
        kind = "open"
        name = json["open"]
    elif "close" in json:
        kind = "close"
        name = json["close"]
    else:
        kind = "standalone"
        name = json["elem"]
    return Markup(
        kind,
        name,
        _options_from_json(json.get("opt", {})),
        json.get("attr", {}),
    )


def _options_from_json(json: dict[str, Any]) -> dict[str, str | VariableRef]:
    return {
        name: value if isinstance(value, str) else VariableRef(value["$"])
        for name, value in json.items()
    }
