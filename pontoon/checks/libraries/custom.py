from collections.abc import Iterable, Iterator
from re import compile, fullmatch
from typing import cast

from fluent.syntax import FluentParser, ast
from fluent.syntax.visitor import Visitor
from moz.l10n.formats.mf2 import mf2_parse_message
from moz.l10n.formats.webext import webext_parse_message, webext_serialize_message
from moz.l10n.model import (
    Expression,
    Markup,
    Message,
    Pattern,
    PatternMessage,
    SelectMessage,
)

from pontoon.base.models import Entity, Resource
from pontoon.base.simple_preview import get_simple_preview, preview_placeholder


parser = FluentParser()


class IsEmptyVisitor(Visitor):
    def __init__(self):
        self.is_empty = False
        self.is_pattern_empty = True

    def visit_Pattern(self, node):
        self.is_pattern_empty = True
        self.visit(node.elements)
        if self.is_pattern_empty:
            self.is_empty = True

    def visit_Placeable(self, node):
        if isinstance(node.expression, ast.Literal):
            if node.expression.parse()["value"]:
                self.is_pattern_empty = False
        elif isinstance(node.expression, ast.SelectExpression):
            self.generic_visit(node.expression)
        else:
            self.is_pattern_empty = False

    def visit_TextElement(self, node):
        if node.value:
            self.is_pattern_empty = False


def run_custom_checks(entity: Entity, string: str) -> dict[str, list[str]]:
    """
    Group all checks related to the base UI that get stored in the DB
    """
    if not string:
        if entity.resource.allows_empty_translations:
            return {"pndbWarnings": ["Empty translation"]}
        else:
            # Prevent empty translation submissions if not supported
            return {"pErrors": ["Empty translations are not allowed"]}

    format = cast(Resource.Format, entity.resource.format)
    errors: list[str] = []
    warnings: list[str] = []
    match format:
        case Resource.Format.ANDROID | Resource.Format.XCODE:
            try:
                msg = mf2_parse_message(string)
            except ValueError as e:
                msg = None
                errors.append(f"Parse error: {e}")
            try:
                orig_msg = mf2_parse_message(entity.string)
            except ValueError as e:
                orig_msg = None
                warnings.append(f"Source parse error: {e}")

            if msg:
                if format == Resource.Format.ANDROID and msg.is_empty():
                    errors.append("Empty translations are not allowed")

                if isinstance(msg, SelectMessage) and not isinstance(
                    orig_msg, SelectMessage
                ):
                    errors.append("Plural translation requires plural source")

                require_printf_placeholders_match(
                    format, orig_msg, msg, errors, warnings
                )

        case Resource.Format.GETTEXT:
            try:
                msg = mf2_parse_message(string)
                patterns = get_patterns(msg)
                if any(all(el == "" for el in pattern) for pattern in patterns):
                    errors.append("Empty translations are not allowed")
            except ValueError as e:
                msg = None
                errors.append(f"Parse error: {e}")

            if isinstance(msg, SelectMessage):
                try:
                    orig_msg = mf2_parse_message(entity.string)
                except ValueError:
                    orig_msg = None
                if not isinstance(orig_msg, SelectMessage):
                    errors.append("Plural translation requires plural source")

            # Bug 1599056: Original and translation must either both end in a newline,
            # or none of them should.
            if entity.string.endswith("\n") != string.endswith("\n"):
                errors.append("Ending newline mismatch")

        case Resource.Format.FLUENT:
            translation_ast = parser.parse_entry(string)
            entity_ast = parser.parse_entry(entity.string)

            # Parse error
            if isinstance(translation_ast, ast.Junk):
                errors.append(translation_ast.annotations[0].message)

            # Not a localizable entry
            elif not isinstance(translation_ast, (ast.Message, ast.Term)):
                errors.append("Translation needs to be a valid localizable entry")

            # Message ID mismatch
            elif entity_ast.id.name != translation_ast.id.name:
                errors.append("Translation key needs to match source string key")

            # Empty translation entry warning; set here rather than pontoon_non_db.py
            # to avoid needing to parse the Fluent message twice.
            else:
                visitor = IsEmptyVisitor()
                visitor.visit(translation_ast)
                if visitor.is_empty:
                    warnings.append("Empty translation")

        case Resource.Format.WEBEXT:
            try:
                msg = mf2_parse_message(string)
            except ValueError as e:
                msg = None
                errors.append(f"Parse error: {e}")
            if isinstance(msg, PatternMessage):
                try:
                    orig_msg = mf2_parse_message(entity.string)
                    _, placeholders = webext_serialize_message(orig_msg)
                except ValueError:
                    placeholders = None

                # The default moz.l10n serialization would escape $ in literal content,
                # which we don't want here -- instead looking for typos in placeholders.
                webext_src = ""
                for part in msg.pattern:
                    if isinstance(part, str):
                        webext_src += part
                    else:
                        part_source = part.attributes.get("source", None)
                        if isinstance(part_source, str):
                            webext_src += part_source
                        else:
                            errors.append(f"Unsupported placeholder: {part}")
                try:
                    webext_parse_message(webext_src, placeholders)
                except Exception as e:
                    bad_ph = fullmatch(r"Missing placeholders entry for (\w+)", str(e))
                    errors.append(
                        f"Placeholder ${bad_ph.group(1).upper()}$ not found in reference"
                        if bad_ph
                        else f"Parse error: {e}"
                    )

    checks: dict[str, list[str]] = {}
    if errors:
        checks["pErrors"] = errors
    if warnings:
        checks["pndbWarnings"] = warnings
    return checks


# Matches all HTML/XML elements and Android & Xcode printf specifiers
ph_re = compile(
    r"<[^>]+>|%#@\w+@|%(?:[1-9]\$|<)?[-#+ 0,(]?[0-9.]*(?:hh?|ll?|[qztjLT])?.?"
)


def require_printf_placeholders_match(
    format: Resource.Format,
    src: Message | None,
    tgt: Message,
    errors: list[str],
    warnings: list[str],
) -> None:
    src_ph_strings: set[str] = set()
    if src:
        for pattern in get_patterns(src):
            for el in pattern:
                if isinstance(el, str):
                    if "%" in el:
                        # If the bare text includes a %, presumably the message is not going
                        # to be printf-formatted, and so we can exit early.
                        return
                elif not (
                    isinstance(el, Expression)
                    and isinstance(el.arg, str)
                    and el.function is None
                ):
                    src_ph_strings.add(preview_placeholder(el))

    found_ph: set[str] = set()
    for pattern in get_patterns(tgt):
        pat_src = get_simple_preview(format, pattern)

        for pm in ph_re.finditer(pat_src):
            rest = pat_src[pm.start() :]
            for ph in src_ph_strings:
                if rest.startswith(ph):
                    found_ph.add(ph)
                    break
            else:
                ph = pm[0]
                if ph not in {"%%", "%n"}:
                    kind = "Element" if ph.startswith("<") else "Placeholder"
                    errors.append(f"{kind} {ph} not found in reference")

    for ph in src_ph_strings:
        if ph not in found_ph:
            kind = "Element" if ph.startswith("<") else "Placeholder"
            warnings.append(f"{kind} {ph} not found in translation")


def get_patterns(msg: Message) -> Iterable[Pattern]:
    return (msg.pattern,) if isinstance(msg, PatternMessage) else msg.variants.values()


def get_placeholders(patterns: Iterable[Pattern]) -> Iterator[Expression | Markup]:
    return (el for pattern in patterns for el in pattern if not isinstance(el, str))
