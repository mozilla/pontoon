from html import escape
from typing import Iterable, Iterator

from fluent.syntax import FluentParser, ast
from fluent.syntax.visitor import Visitor
from moz.l10n.formats.android import android_parse_message
from moz.l10n.formats.mf2 import mf2_parse_message
from moz.l10n.model import (
    Expression,
    Markup,
    Message,
    Pattern,
    PatternMessage,
    SelectMessage,
)

from pontoon.base.models import Entity, Resource
from pontoon.base.simple_preview import (
    android_placeholder_preview,
    android_simple_preview,
)


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

    errors: list[str] = []
    warnings: list[str] = []
    match entity.resource.format:
        case Resource.Format.ANDROID:
            try:
                msg = mf2_parse_message(string)
                patterns = get_patterns(msg)
            except ValueError as e:
                msg = None
                patterns = ()
                errors.append(f"Parse error: {e}")
            try:
                orig_msg = mf2_parse_message(entity.string)
                orig_ph_iter = (
                    el
                    for pattern in get_patterns(orig_msg)
                    for el in pattern
                    if not isinstance(el, str)
                )
                orig_ps = {android_placeholder_preview(ph) for ph in orig_ph_iter}
            except ValueError:
                orig_msg = None
                orig_ps = set()

            if any(all(el == "" for el in pattern) for pattern in patterns):
                errors.append("Empty translations are not allowed")

            if isinstance(msg, SelectMessage) and not isinstance(
                orig_msg, SelectMessage
            ):
                errors.append("Plural translation requires plural source")

            # Inlined Android checks from compare-locales to support <plurals>
            found_ps: set[str] = set()
            try:
                for pattern in patterns:
                    android_msg = android_parse_message(
                        escape(android_simple_preview(pattern))
                    )
                    for el in android_msg.pattern:
                        if not isinstance(el, str):
                            ps = android_placeholder_preview(el)
                            if ps in orig_ps:
                                found_ps.add(ps)
                            else:
                                errors.append(
                                    f"Placeholder {ps} not found in reference"
                                )
                for ps in orig_ps:
                    if ps not in found_ps:
                        warnings.append(f"Placeholder {ps} not found in translation")
            except Exception as e:
                errors.append(f"Parse error: {e}")

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

    checks: dict[str, list[str]] = {}
    if errors:
        checks["pErrors"] = errors
    if warnings:
        checks["pndbWarnings"] = warnings
    return checks


def get_patterns(msg: Message) -> Iterable[Pattern]:
    return (msg.pattern,) if isinstance(msg, PatternMessage) else msg.variants.values()


def get_placeholders(patterns: Iterable[Pattern]) -> Iterator[Expression | Markup]:
    return (el for pattern in patterns for el in pattern if not isinstance(el, str))
