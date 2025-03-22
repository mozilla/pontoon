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

from collections.abc import Iterable, Mapping
from functools import cmp_to_key
from re import compile
from typing import Literal

from ...model import (
    CatchallKey,
    Expression,
    Markup,
    Pattern,
    PatternMessage,
    SelectMessage,
    VariableRef,
)

_name_start = r"a-zA-Z_\xC0-\xD6\xD8-\xF6\xF8-\u02FF\u0370-\u037D\u037F-\u061B\u061D-\u1FFF\u200C-\u200D\u2070-\u218F\u2C00-\u2FEF\u3001-\uD7FF\uF900-\uFDCF\uFDF0-\uFFFC\U00010000-\U000EFFFF"
name_re = compile(f"[{_name_start}][{_name_start}0-9-.\xb7\u0300-\u036f\u203f-\u2040]*")
identifier_re = compile(f"{name_re.pattern}(?::{name_re.pattern})?")
number_re = compile(r"-?(?:0|(?:[1-9]\d*))(?:.\d+)?(?:[eE][-+]?\d+)?")


class MF2ValidationError(ValueError):
    pass


def mf2_validate_message(msg: PatternMessage | SelectMessage) -> None:
    """
    Validate that the message satisfies MessageFormat 2 validity constraints.

    May reorder declarations.

    May raise `MF2ValidationError`.
    """
    if isinstance(msg, PatternMessage):
        _validate_declarations(msg.declarations)
        _validate_pattern(msg.pattern)
    elif isinstance(msg, SelectMessage):
        _validate_declarations(msg.declarations)
        if not msg.selectors or not isinstance(msg.selectors, tuple):
            raise MF2ValidationError(f"Invalid selectors: {msg.selectors}")
        for sel in msg.selectors:
            if isinstance(sel, VariableRef):
                _validate_variable(sel)
            else:
                raise MF2ValidationError(f"Invalid selector: {sel}")
            sel_name = sel.name
            sel_expr = msg.declarations.get(sel_name, None)
            while sel_expr is not None and sel_expr.function is None:
                if (
                    isinstance(sel_expr.arg, VariableRef)
                    and sel_expr.arg.name != sel_name
                ):
                    sel_name = sel_expr.arg.name
                    sel_expr = msg.declarations.get(sel_name, None)
                else:
                    sel_expr = None
            if sel_expr is None:
                raise MF2ValidationError(
                    msg, f"Missing selector annotation for ${sel.name}"
                )
        sel_count = len(msg.selectors)
        if not isinstance(msg.variants, Mapping):
            raise MF2ValidationError(f"Invalid variants: {msg.variants}")
        for keys, pattern in msg.variants.items():
            if not isinstance(keys, tuple):
                raise MF2ValidationError(f"Invalid keys: {keys}")
            for key in keys:
                if not isinstance(key, str) and not isinstance(key, CatchallKey):
                    raise MF2ValidationError(f"Invalid key: {key}")
            if len(keys) != sel_count:
                raise MF2ValidationError(
                    f"Variant key mismatch, expected {sel_count} but found {len(keys)}",
                )
            _validate_pattern(pattern)
        if (CatchallKey(),) * sel_count not in msg.variants:
            raise MF2ValidationError("Missing fallback variant")
    else:
        raise MF2ValidationError(f"Invalid message: {msg}")


def _validate_declarations(declarations: dict[str, Expression]) -> None:
    decl_data: list[tuple[str, bool]] = []
    dependencies: dict[str, set[str]] = {}

    def deep_dependencies(name: str, res: set[str]) -> set[str]:
        if name in dependencies:
            for dep in dependencies[name]:
                if dep not in res:
                    res.add(dep)
                    deep_dependencies(dep, res)
        return res

    def cmp_decl_data(a: tuple[str, bool], b: tuple[str, bool]) -> int:
        a_name, a_input = a
        b_name, b_input = b
        if a_name in dependencies[b_name]:
            return -1
        if b_name in dependencies[a_name]:
            return 1
        if a_input != b_input:
            return -1 if a_input else 1
        return -1 if a_name < b_name else 1

    if not isinstance(declarations, Mapping):
        raise MF2ValidationError(f"Invalid declarations: {declarations}")
    for name, expr in declarations.items():
        if not isinstance(name, str) or not name_re.fullmatch(name):
            raise MF2ValidationError(f"Invalid declaration name: {name}")
        if not isinstance(expr, Expression):
            raise MF2ValidationError(f"Invalid declaration expression: {expr}")
        _validate_expression(expr)
        var_name = expr.arg.name if isinstance(expr.arg, VariableRef) else None
        is_input = var_name == name
        decl_data.append((name, is_input))
        deps: set[str] = set()
        if var_name is not None and not is_input:
            deps.add(var_name)
        for opt in expr.options.values():
            if isinstance(opt, VariableRef):
                deps.add(opt.name)
        dependencies[name] = deps

    for name in dependencies:
        deps = deep_dependencies(name, set())
        if name in deps:
            raise MF2ValidationError(f"Duplicate declaration for ${name}")
        dependencies[name] = deps

    if len(declarations) > 1:
        decl_data.sort(key=cmp_to_key(cmp_decl_data))
        inserts = [(name, declarations.pop(name)) for name, _ in decl_data[1:]]
        for name, expr in inserts:
            declarations[name] = expr


def _validate_pattern(pattern: Pattern) -> None:
    if not isinstance(pattern, Iterable) or isinstance(pattern, str):
        raise MF2ValidationError(f"Invalid pattern: {pattern}")
    for part in pattern:
        if isinstance(part, Expression):
            _validate_expression(part)
        elif isinstance(part, Markup):
            _validate_markup(part)
        elif not isinstance(part, str):
            raise MF2ValidationError(f"Invalid pattern part: {part}")


def _validate_expression(expr: Expression) -> None:
    if isinstance(expr.arg, VariableRef):
        _validate_variable(expr.arg)
    elif expr.arg is not None and not isinstance(expr.arg, str):
        raise MF2ValidationError(f"Invalid expression operand: {expr.arg}")
    if expr.function is None:
        if expr.arg is None:
            raise MF2ValidationError(
                "Invalid expression with no operand and no function"
            )
        if expr.options:
            raise MF2ValidationError("Invalid expression with options but no function")
    elif isinstance(expr.function, str) and identifier_re.fullmatch(expr.function):
        _validate_options(expr.options)
    else:
        raise MF2ValidationError(f"Invalid function name: {expr.function}")
    _validate_attributes(expr.attributes)


def _validate_markup(markup: Markup) -> None:
    if markup.kind not in {"open", "standalone", "close"}:
        raise MF2ValidationError(f"Invalid markup kind: {markup.kind}")
    if not isinstance(markup.name, str) or not identifier_re.fullmatch(markup.name):
        raise MF2ValidationError(f"Invalid markup name: {markup.name}")
    _validate_options(markup.options)
    _validate_attributes(markup.attributes)


def _validate_options(options: dict[str, str | VariableRef]) -> None:
    if not isinstance(options, Mapping):
        raise MF2ValidationError(f"Invalid options: {options}")
    for name, value in options.items():
        if not isinstance(name, str) or not identifier_re.fullmatch(name):
            raise MF2ValidationError(f"Invalid option name: {name}")
        if isinstance(value, VariableRef):
            _validate_variable(value)
        elif not isinstance(value, str):
            raise MF2ValidationError(f"Invalid option value: {value}")


def _validate_attributes(attributes: dict[str, str | Literal[True]]) -> None:
    if not isinstance(attributes, Mapping):
        raise MF2ValidationError(f"Invalid attributes: {attributes}")
    for name, value in attributes.items():
        if not isinstance(name, str) or not identifier_re.fullmatch(name):
            raise MF2ValidationError(f"Invalid attribute name: {name}")
        elif value is not True and not isinstance(value, str):
            raise MF2ValidationError(f"Invalid option value: {value}")


def _validate_variable(var: VariableRef) -> None:
    if not isinstance(var.name, str) or not name_re.fullmatch(var.name):
        raise MF2ValidationError(f"Invalid variable name: {var.name}")
