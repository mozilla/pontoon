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
from re import compile
from typing import Literal

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
from .validate import name_re, number_re

complex_start_re = compile(r"[\t\n\r \u3000]*\.")
literal_esc_re = compile(r"[\\|]")
text_esc_re = compile(r"[\\{}]")


def mf2_serialize_message(message: Message) -> Iterator[str]:
    """
    Serialize a message using MessageFormat 2 syntax.

    Does not validate the message before serialization;
    for that, use `mf2_validate_message()`.
    """
    if (
        isinstance(message, PatternMessage)
        and not message.declarations
        and (
            not message.pattern
            or not isinstance(part0 := message.pattern[0], str)
            or not complex_start_re.match(part0)
        )
    ):
        # simple message
        yield from mf2_serialize_pattern(message.pattern)
        return

    for name, expr in message.declarations.items():
        # TODO: Fix order by dependencies
        if isinstance(expr.arg, VariableRef) and expr.arg.name == name:
            yield ".input "
        else:
            yield f".local ${name} = "
        yield from _expression(expr)
        yield "\n"

    if isinstance(message, PatternMessage):
        yield from _quoted_pattern(message.pattern)
    else:
        assert isinstance(message, SelectMessage)
        yield ".match"
        for sel in message.selectors:
            yield f" ${sel.name}"
        for keys, pattern in message.variants.items():
            yield "\n"
            for key in keys:
                yield ("* " if isinstance(key, CatchallKey) else f"{_literal(key)} ")
            yield from _quoted_pattern(pattern)


def mf2_serialize_pattern(pattern: Pattern) -> Iterator[str]:
    if not pattern:
        yield ""
    for part in pattern:
        if isinstance(part, Expression):
            yield from _expression(part)
        elif isinstance(part, Markup):
            yield from _markup(part)
        else:
            assert isinstance(part, str)
            yield text_esc_re.sub(r"\\\g<0>", part)


def _quoted_pattern(pattern: Pattern) -> Iterator[str]:
    yield "{{"
    yield from mf2_serialize_pattern(pattern)
    yield "}}"


def _expression(expr: Expression) -> Iterator[str]:
    yield "{"
    if expr.arg:
        yield _value(expr.arg)
    if expr.function:
        yield f" :{expr.function}" if expr.arg else f":{expr.function}"
    yield from _options(expr.options)
    yield from _attributes(expr.attributes)
    yield "}"


def _markup(markup: Markup) -> Iterator[str]:
    yield "{/" if markup.kind == "close" else "{#"
    yield markup.name
    yield from _options(markup.options)
    yield from _attributes(markup.attributes)
    yield "/}" if markup.kind == "standalone" else "}"


def _options(options: dict[str, str | VariableRef]) -> Iterator[str]:
    for name, value in options.items():
        yield f" {name}={_value(value)}"


def _attributes(attributes: dict[str, str | Literal[True]]) -> Iterator[str]:
    for name, value in attributes.items():
        yield f" @{name}" if value is True else f" @{name}={_literal(value)}"


def _value(value: str | VariableRef) -> str:
    return _literal(value) if isinstance(value, str) else f"${value.name}"


def _literal(literal: str) -> str:
    if name_re.fullmatch(literal) or number_re.fullmatch(literal):
        return literal
    esc_literal = literal_esc_re.sub(r"\\\g<0>", literal)
    return f"|{esc_literal}|"
