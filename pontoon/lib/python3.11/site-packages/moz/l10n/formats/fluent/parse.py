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

from collections.abc import Generator
from itertools import product
from re import finditer
from typing import Any, Literal, Tuple, cast, overload

from fluent.syntax import FluentParser
from fluent.syntax import ast as ftl

from ...model import (
    CatchallKey,
    Comment,
    Entry,
    Expression,
    LinePos,
    Message,
    Metadata,
    Pattern,
    PatternMessage,
    Resource,
    Section,
    SelectMessage,
    VariableRef,
)
from .. import Format


@overload
def fluent_parse(
    source: bytes | str | ftl.Resource,
    *,
    as_ftl_patterns: Literal[False] = False,
    with_linepos: bool = True,
) -> Resource[Message]: ...


@overload
def fluent_parse(
    source: bytes | str | ftl.Resource,
    *,
    as_ftl_patterns: Literal[True],
    with_linepos: bool = True,
) -> Resource[ftl.Pattern]: ...


def fluent_parse(
    source: bytes | str | ftl.Resource,
    *,
    as_ftl_patterns: bool = False,
    with_linepos: bool = True,
) -> Resource[Message] | Resource[ftl.Pattern]:
    """
    Parse a .ftl file into a message resource.

    Message and term references are represented by `message` function annotations,
    with term identifiers prefixed with a `-`.

    By default, messages are parsed as Messages;
    to keep them as Fluent Patterns, use `as_ftl_patterns=True`.

    Function names are lower-cased, so e.g. the Fluent `NUMBER` is `number` in the Resource.

    The parsed resource will not include any metadata.
    """

    if isinstance(source, ftl.Resource):
        fluent_res = source
        lpm = None  # Source is required for line positions
    else:
        source_str = source if isinstance(source, str) else source.decode("utf-8")
        fluent_res = FluentParser(with_spans=with_linepos).parse(source_str)
        lpm = LinePosMapper(source_str) if with_linepos else None

    entries: list[Entry[Any] | Comment] = []
    section = Section((), entries)
    resource = Resource(Format.fluent, [section])
    fluent_body = fluent_res.body
    if fluent_body and isinstance(fbc := fluent_body[0], ftl.Comment) and fbc.content:
        resource.meta.append(Metadata("info", fbc.content))
        fluent_body = fluent_body[1:]
    for entry in fluent_body:
        if isinstance(entry, ftl.Message) or isinstance(entry, ftl.Term):
            entries.extend(patterns(entry, as_ftl_patterns, lpm))
        elif isinstance(entry, ftl.ResourceComment):
            if entry.content:
                resource.comment = (
                    (resource.comment.rstrip() + "\n\n" + entry.content)
                    if resource.comment
                    else entry.content
                )
        elif isinstance(entry, ftl.GroupComment):
            if entries or section.comment:
                entries = []
                section = Section((), entries, comment=entry.content or "")
                if lpm and entry.span:
                    span = entry.span
                    section.linepos = lpm.get_linepos(
                        span.start, span.start, span.start, span.end
                    )
                resource.sections.append(section)
            else:
                section.comment = entry.content or ""
                if lpm and entry.span:
                    span = entry.span
                    section.linepos = lpm.get_linepos(
                        span.start, span.start, span.start, span.end
                    )
        elif isinstance(entry, ftl.Comment):
            if entry.content:
                entries.append(Comment(entry.content))
        else:  # Junk
            try:
                message = entry.annotations[0].message
            except Exception:
                message = ""
            raise ValueError(message or "Fluent parser error")
    return resource


def patterns(
    ftl_entry: ftl.Message | ftl.Term,
    as_ftl_patterns: bool,
    lpm: LinePosMapper | None,
) -> Generator[Entry[Message] | Entry[ftl.Pattern], None, None]:
    message = (lambda m: m) if as_ftl_patterns else fluent_parse_message
    id = ftl_entry.id.name
    if isinstance(ftl_entry, ftl.Term):
        id = "-" + id
    comment = ftl_entry.comment.content or "" if ftl_entry.comment else ""
    if ftl_entry.value:
        entry: Entry[Any] = Entry(
            id=(id,), value=message(ftl_entry.value), comment=comment
        )
        if lpm and ftl_entry.span and ftl_entry.value.span:
            v_span = ftl_entry.value.span
            c_span = (
                ftl_entry.comment.span
                if comment and ftl_entry.comment and ftl_entry.comment.span
                else ftl_entry.span
            )
            k_span = ftl_entry.id.span or ftl_entry.span
            entry.linepos = lpm.get_linepos(
                c_span.start, k_span.start, v_span.start, v_span.end
            )
        yield entry
        if comment:
            comment = ""
    for attr in ftl_entry.attributes:
        entry = Entry(id=(id, attr.id.name), value=message(attr.value), comment=comment)
        if lpm and attr.span:
            span = attr.span
            c_span = (
                ftl_entry.comment.span
                if comment and ftl_entry.comment and ftl_entry.comment.span
                else span
            )
            k_span = attr.id.span or span
            v_span = attr.value.span or span
            entry.linepos = lpm.get_linepos(
                c_span.start, k_span.start, v_span.start, span.end
            )
        yield entry
        if comment:
            comment = ""


def fluent_parse_message(ftl_pattern: ftl.Pattern) -> Message:
    sel_data = find_selectors(ftl_pattern, [])
    sel_expressions = [sd[0] for sd in sel_data]
    filter: list[Key | None] = [None] * len(sel_expressions)
    msg_variants: dict[tuple[Key, ...], Pattern]
    var_names: set[str] = set()
    if sel_expressions:
        key_lists = [list(dict.fromkeys(sd[2])) for sd in sel_data]
        for keys in key_lists:
            keys.sort(key=lambda k: (k[2], not k[1]))
        msg_variants = {key: [] for key in product(*key_lists)}
    else:
        msg_variants = {(): []}

    def add_pattern(ftl_pattern: ftl.Pattern) -> None:
        el: (
            ftl.TextElement
            | ftl.Placeable
            | ftl.InlineExpression
            | ftl.SelectExpression
        )
        for el in ftl_pattern.elements:
            while isinstance(el, ftl.Placeable):
                el = el.expression
            if isinstance(el, ftl.SelectExpression):
                msg_sel = next(sd[0] for sd in sel_data if el.selector in sd[1])
                idx = sel_expressions.index(msg_sel)
                prev_filt = filter[idx]
                for v in el.variants:
                    filter[idx] = variant_key(v)
                    add_pattern(v.value)
                filter[idx] = prev_filt
            else:
                for keys, msg_pattern in msg_variants.items():
                    if all(
                        (filt is None or key == filt) for key, filt in zip(keys, filter)
                    ):
                        if isinstance(el, ftl.TextElement):
                            if msg_pattern and isinstance(msg_pattern[-1], str):
                                msg_pattern[-1] += el.value
                            else:
                                msg_pattern.append(el.value)
                        else:
                            expr = inline_expression(el)
                            if isinstance(expr.arg, VariableRef):
                                var_names.add(expr.arg.name)
                            msg_pattern.append(expr)

    add_pattern(ftl_pattern)

    if sel_expressions:
        declarations = {}
        selectors = []
        for expr in sel_expressions:
            stem = expr.arg.name if isinstance(expr.arg, VariableRef) else ""
            i = 0
            name = stem
            while name in var_names or name == "":
                i += 1
                name = f"{stem}_{i}"
            declarations[name] = expr
            selectors.append(VariableRef(name))
            var_names.add(name)
        variants = {
            tuple(map(message_key, keys)): msg_pattern
            for keys, msg_pattern in msg_variants.items()
            if msg_pattern
        }
        return SelectMessage(declarations, tuple(selectors), variants)
    else:
        return PatternMessage(next(iter(msg_variants.values())))


Key = Tuple[str, bool, bool]
"(name, is_numeric, is_default)"


def variant_key(v: ftl.Variant) -> Key:
    name: str
    is_numeric: bool
    if isinstance(v.key, ftl.Identifier):
        name = v.key.name
        is_numeric = False
    else:
        name = v.key.value
        is_numeric = True
    return (name, is_numeric, v.default)


def message_key(key: Key) -> str | CatchallKey:
    name, _, is_default = key
    return CatchallKey(name) if is_default else name


def find_selectors(
    pattern: ftl.Pattern,
    result: list[tuple[Expression, list[ftl.InlineExpression], list[Key]]],
) -> list[tuple[Expression, list[ftl.InlineExpression], list[Key]]]:
    for el in pattern.elements:
        if isinstance(el, ftl.Placeable) and isinstance(
            el.expression, ftl.SelectExpression
        ):
            ftl_sel = el.expression.selector
            keys = [variant_key(v) for v in el.expression.variants]
            msg_sel = select_expression(ftl_sel, keys)
            prev = next((x for x in result if x[0] == msg_sel), None)
            if prev:
                _, ftl_list, key_list = prev
                ftl_list.append(ftl_sel)
                key_list += keys
            else:
                result.append((msg_sel, [ftl_sel], keys))
            for v in el.expression.variants:
                find_selectors(v.value, result)
    return result


def select_expression(ftl_sel: ftl.InlineExpression, keys: list[Key]) -> Expression:
    plural_categories = ("zero", "one", "two", "few", "many", "other")
    if isinstance(ftl_sel, ftl.VariableReference):
        name = (
            "number"
            if all(
                is_numeric or name in plural_categories for name, is_numeric, _ in keys
            )
            else "string"
        )
        return Expression(VariableRef(ftl_sel.id.name), name)
    elif isinstance(ftl_sel, ftl.StringLiteral):
        return Expression(literal_value(ftl_sel), "string")
    else:
        return inline_expression(ftl_sel)


def inline_expression(exp: ftl.InlineExpression) -> Expression:
    if isinstance(exp, ftl.NumberLiteral):
        value = exp.value
        return Expression(value, "number")
    elif isinstance(exp, ftl.StringLiteral):
        value = exp.parse().get("value") or ""
        return Expression(value)
    elif isinstance(exp, ftl.MessageReference):
        name = exp.id.name
        if exp.attribute is not None:
            name += "." + exp.attribute.name
        return Expression(name, "message")
    elif isinstance(exp, ftl.TermReference):
        name = "-" + exp.id.name
        if exp.attribute is not None:
            name += "." + exp.attribute.name
        ftl_named = exp.arguments.named if exp.arguments else []
        return Expression(
            name,
            "message",
            {opt.name.name: literal_value(opt.value) for opt in ftl_named},
        )
    elif isinstance(exp, ftl.VariableReference):
        name = exp.id.name
        return Expression(VariableRef(name))
    else:  # ftl.FunctionReference
        name = exp.id.name.lower()
        if len(exp.arguments.positional) > 1:
            raise ValueError(
                f"Functions with more than one positional argument are not supported: {name}"
            )
        ftl_arg: ftl.Placeable | ftl.InlineExpression | None = next(
            iter(exp.arguments.positional), None
        )
        while isinstance(ftl_arg, ftl.Placeable):
            ftl_arg = cast(ftl.InlineExpression, ftl_arg.expression)
        arg: str | VariableRef | None
        if not ftl_arg:
            arg = None
        elif isinstance(ftl_arg, ftl.NumberLiteral) or isinstance(
            ftl_arg, ftl.StringLiteral
        ):
            arg = literal_value(ftl_arg)
        elif isinstance(ftl_arg, ftl.VariableReference):
            arg = VariableRef(ftl_arg.id.name)
        else:
            raise ValueError(f"Unexpected value: {ftl_arg}")
        ftl_named = exp.arguments.named
        return Expression(
            arg,
            name,
            {opt.name.name: literal_value(opt.value) for opt in ftl_named},
        )


def literal_value(arg: ftl.NumberLiteral | ftl.StringLiteral) -> str:
    return (
        arg.value
        if isinstance(arg, ftl.NumberLiteral)
        else arg.parse().get("value") or ""
    )


class LinePosMapper:
    def __init__(self, src: str) -> None:
        self._len = len(src)
        self._newlines = [m.start() for m in finditer("\n", src)]

    def _get_line(self, char_idx: int) -> int:
        # Treat the end of the string as a newline.
        if not self._newlines and char_idx >= self._len:
            return 2
        return next(
            (idx + 1 for idx, nl in enumerate(self._newlines) if nl > char_idx),
            len(self._newlines) + 1,
        )

    def get_linepos(self, start: int, key: int, value: int, end: int) -> LinePos:
        start_line = self._get_line(start)
        key_line = start_line if key == start else self._get_line(key)
        value_line = key_line if value == key else self._get_line(value)
        end_line = self._get_line(end)
        return LinePos(start_line, key_line, value_line, end_line)
