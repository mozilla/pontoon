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

esc_chars = {"\\", "{", "|", "}"}

bidi_chars = {
    "\u061c",  # ALM
    "\u200e",  # LRM
    "\u200f",  # RLM
    "\u2066",  # LRI
    "\u2067",  # RLI
    "\u2068",  # FSI
    "\u2069",  # PDI
}

space_chars = {
    "\t",
    "\n",
    "\r",
    " ",
    "\u3000",  # ideographic space
}


def mf2_parse_message(source: bytes | str) -> Message:
    """
    Parse MF2 message syntax into a Message.

    May raise `MF2ParseError`.
    """
    if not isinstance(source, str):
        source = source.decode()
    parser = MF2Parser(source)
    return parser.parse()


class MF2ParseError(ValueError):
    def __init__(self, parser: MF2Parser, message: str):
        src = parser.source.replace("\n", "¶")
        message += f"\n{src}\n{' '*parser.pos}^"
        super().__init__(message)
        self.pos = parser.pos


class MF2Parser:
    def __init__(self, source: bytes | str):
        self.source = source if isinstance(source, str) else source.decode()
        self.pos = 0

    def parse(self) -> Message:
        ch = self.skip_opt_space()
        if ch == ".":
            message = self.complex_message()
        elif self.source.startswith("{{", self.pos):
            message = PatternMessage(self.quoted_pattern())
        else:
            self.pos = 0
            message = PatternMessage(self.pattern())
        if self.pos != len(self.source):
            raise MF2ParseError(self, "Extra content at message end")
        return message

    def complex_message(self) -> Message:
        assert self.char() == "."
        declarations: dict[str, Expression] = {}
        declared: set[str] = set()
        while keyword := self.source[self.pos : self.pos + 6]:
            if keyword == ".input":
                name, expr = self.input_declaration()
            elif keyword == ".local":
                name, expr = self.local_declaration()
                if isinstance(expr.arg, VariableRef):
                    declared.add(expr.arg.name)
            else:
                break
            if expr.function:
                for opt_value in expr.options.values():
                    if isinstance(opt_value, VariableRef):
                        declared.add(opt_value.name)
            if name in declared:
                raise MF2ParseError(self, f"Duplicate declaration for ${name}")
            declarations[name] = expr
            declared.add(name)
            self.skip_opt_space()
        if keyword == ".match":
            selectors = self.match_statement()
            for sel in selectors:
                sel_name = sel.name
                sel_expr = declarations.get(sel_name, None)
                while sel_expr is not None and sel_expr.function is None:
                    if (
                        isinstance(sel_expr.arg, VariableRef)
                        and sel_expr.arg.name != sel_name
                    ):
                        sel_name = sel_expr.arg.name
                        sel_expr = declarations.get(sel_name, None)
                    else:
                        sel_expr = None
                if sel_expr is None:
                    raise MF2ParseError(
                        self, f"Missing selector annotation for ${sel.name}"
                    )
            variants = {}
            while self.pos < len(self.source):
                keys, pattern = self.variant(len(selectors))
                if keys in variants:
                    raise MF2ParseError(self, f"Duplicate variant with key ${keys}")
                variants[keys] = pattern
            fallback_key = (CatchallKey(),) * len(selectors)
            if fallback_key not in variants:
                raise MF2ParseError(self, "Missing fallback variant")
            return SelectMessage(declarations, selectors, variants)
        pattern = self.quoted_pattern()
        return PatternMessage(pattern, declarations)

    def input_declaration(self) -> tuple[str, Expression]:
        assert self.source.startswith(".input", self.pos)
        self.pos += 6
        ch = self.skip_opt_space()
        self.expect("{", ch)
        expr = self.expression_or_markup()
        if not isinstance(expr, Expression) or not isinstance(expr.arg, VariableRef):
            raise MF2ParseError(self, "Variable argument required for .input")
        return expr.arg.name, expr

    def local_declaration(self) -> tuple[str, Expression]:
        assert self.source.startswith(".local", self.pos)
        self.pos += 6
        if not self.req_space() or self.char() != "$":
            raise MF2ParseError(self, "Expected $ with leading space")
        name = self.name(1)
        ch = self.skip_opt_space()
        self.expect("=", ch)
        ch = self.skip_opt_space()
        self.expect("{", ch)
        expr = self.expression_or_markup()
        if not isinstance(expr, Expression):
            raise MF2ParseError(self, "Markup is not a valid .local value")
        if isinstance(expr.arg, VariableRef) and expr.arg.name == name:
            raise MF2ParseError(self, "A .local declaration cannot be self-referential")
        return name, expr

    def match_statement(self) -> tuple[VariableRef, ...]:
        assert self.source.startswith(".match", self.pos)
        self.pos += 6
        names: list[str] = []
        while (has_space := self.req_space()) and self.char() == "$":
            names.append(self.name(1))
        if not names:
            raise MF2ParseError(
                self, "At least one variable reference is required for .match"
            )
        if not has_space:
            raise MF2ParseError(self, "Expected space")
        return tuple(VariableRef(name) for name in names)

    def variant(self, num_sel: int) -> tuple[tuple[str | CatchallKey, ...], Pattern]:
        keys: list[str | CatchallKey] = []
        ch = self.char()
        while ch != "{" and ch != "":
            if ch == "*":
                keys.append(CatchallKey())
                self.pos += 1
            else:
                keys.append(self.literal())
            has_space = self.req_space()
            if not has_space:
                break
            ch = self.char()
        if len(keys) != num_sel:
            raise MF2ParseError(
                self,
                f"Variant key mismatch, expected {num_sel} but found {len(keys)}",
            )
        return tuple(keys), self.quoted_pattern()

    def quoted_pattern(self) -> Pattern:
        if not self.source.startswith("{{", self.pos):
            raise MF2ParseError(self, "Expected {{")
        self.pos += 2
        pattern = self.pattern()
        if not self.source.startswith("}}", self.pos):
            raise MF2ParseError(self, "Expected }}")
        self.pos += 2
        self.skip_opt_space()
        return pattern

    def pattern(self) -> Pattern:
        pattern: Pattern = []
        ch = self.char()
        while ch != "" and ch != "}":
            if ch == "{":
                self.pos += 1
                pattern.append(self.expression_or_markup())
            else:
                pattern.append(self.text())
            ch = self.char()
        return pattern

    def text(self) -> str:
        text = ""
        at_esc = False
        for ch in self.source[self.pos :]:
            if at_esc:
                if ch not in esc_chars:
                    raise MF2ParseError(self, f"Invalid escape: \\{ch}")
                text += ch
                at_esc = False
            elif ch == "\x00":
                raise MF2ParseError(self, "NUL character is not allowed")
            elif ch == "\\":
                at_esc = True
            elif ch == "{" or ch == "}":
                break
            else:
                text += ch
            self.pos += 1
        return text

    def expression_or_markup(self) -> Expression | Markup:
        ch = self.skip_opt_space()
        value: Expression | Markup = (
            self.markup_body(ch) if ch == "#" or ch == "/" else self.expression_body(ch)
        )
        self.expect("}")
        return value

    def expression_body(self, ch: str) -> Expression:
        arg: str | VariableRef | None = None
        arg_end = self.pos
        if ch == "$":
            arg = self.variable()
            arg_end = self.pos
            ch = self.skip_opt_space()
        elif ch != ":":
            arg = self.literal()
            arg_end = self.pos
            ch = self.skip_opt_space()
        if ch == ":":
            if arg and self.pos == arg_end:
                raise MF2ParseError(self, "Expected space")
            function = self.identifier(1)
            options = self.options()
        else:
            function = None
            options = {}
            self.pos = arg_end
        attributes = self.attributes()
        self.skip_opt_space()
        return Expression(arg, function, options, attributes)

    def markup_body(self, ch: str) -> Markup:
        kind: Literal["open", "standalone", "close"]
        if ch == "#":
            kind = "open"
        elif ch == "/":
            kind = "close"
        else:
            raise MF2ParseError(self, "Expected # or /")
        id = self.identifier(1)
        options = self.options()
        attributes = self.attributes()
        ch = self.skip_opt_space()
        if ch == "/":
            if kind == "open":
                kind = "standalone"
            else:
                raise MF2ParseError(self, "Expected }")
            self.pos += 1
        return Markup(kind, id, options, attributes)

    def options(self) -> dict[str, str | VariableRef]:
        options: dict[str, str | VariableRef] = {}
        opt_end = self.pos
        while self.req_space():
            ch = self.char()
            if ch == "" or ch == "@" or ch == "/" or ch == "}":
                self.pos = opt_end
                break
            id = self.identifier(0)
            if id in options:
                raise MF2ParseError(self, f"Duplicate option name {id}")
            self.expect("=", self.skip_opt_space())
            ch = self.skip_opt_space()
            options[id] = self.variable() if ch == "$" else self.literal()
            opt_end = self.pos
        return options

    def attributes(self) -> dict[str, str | Literal[True]]:
        attributes: dict[str, str | Literal[True]] = {}
        attr_end = self.pos
        while self.req_space():
            ch = self.char()
            if ch != "@":
                self.pos = attr_end
                break
            id = self.identifier(1)
            id_end = self.pos
            if id in attributes:
                raise MF2ParseError(self, f"Duplicate attribute name {id}")
            if self.skip_opt_space() == "=":
                self.pos += 1
                self.skip_opt_space()
                attributes[id] = self.literal()
            else:
                self.pos = id_end
                attributes[id] = True
            attr_end = self.pos
        return attributes

    def variable(self) -> VariableRef:
        assert self.char() == "$"
        name = self.name(1)
        return VariableRef(name)

    def literal(self) -> str:
        return self.quoted_literal() if self.char() == "|" else self.unquoted_literal()

    def quoted_literal(self) -> str:
        assert self.char() == "|"
        self.pos += 1
        value = ""
        at_esc = False
        for ch in self.source[self.pos :]:
            self.pos += 1
            if at_esc:
                if ch not in esc_chars:
                    raise MF2ParseError(self, f"Invalid escape: \\{ch}")
                value += ch
                at_esc = False
            elif ch == "\x00":
                raise MF2ParseError(self, "NUL character is not allowed")
            elif ch == "\\":
                at_esc = True
            elif ch == "|":
                return value
            else:
                value += ch
        raise MF2ParseError(self, "Expected |")

    def unquoted_literal(self) -> str:
        match = number_re.match(self.source, self.pos) or name_re.match(
            self.source, self.pos
        )
        if match is None:
            raise MF2ParseError(self, "Invalid name or number")
        self.pos = match.end()
        return match[0]

    def identifier(self, offset: int) -> str:
        ns = self.name(offset)
        if self.char() != ":":
            return ns
        name = self.name(1)
        return f"{ns}:{name}"

    def name(self, offset: int) -> str:
        self.pos += offset
        self.skip_bidi()
        match = name_re.match(self.source, self.pos)
        if match is None:
            raise MF2ParseError(self, "Invalid name")
        self.pos = match.end()
        self.skip_bidi()
        return match[0]

    def req_space(self) -> bool:
        start = self.pos
        ch = self.skip_bidi()
        if ch not in space_chars:
            self.pos = start
            return False
        while ch in space_chars or ch in bidi_chars:
            self.pos += 1
            ch = self.char()
        return True

    def skip_opt_space(self) -> str:
        ch = self.char()
        while ch in space_chars or ch in bidi_chars:
            self.pos += 1
            ch = self.char()
        return ch

    def skip_bidi(self) -> str:
        """Bidirectional marks and isolates"""
        ch = self.char()
        while ch in bidi_chars:
            self.pos += 1
            ch = self.char()
        return ch

    def expect(self, exp: str, char: str = "") -> None:
        if (char or self.char()) != exp:
            raise MF2ParseError(self, f"Expected {exp}")
        self.pos += 1

    def char(self) -> str:
        try:
            return self.source[self.pos]
        except IndexError:
            return ""
