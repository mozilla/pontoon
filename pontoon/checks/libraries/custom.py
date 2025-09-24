from fluent.syntax import FluentParser, ast
from fluent.syntax.visitor import Visitor
from moz.l10n.formats.mf2 import mf2_parse_message
from moz.l10n.model import PatternMessage, SelectMessage

from pontoon.base.models import Entity, Resource


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


def run_custom_checks(
    entity: Entity, original: str, string: str
) -> dict[str, list[str]]:
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
        case Resource.Format.ANDROID | Resource.Format.GETTEXT:
            try:
                msg = mf2_parse_message(string)
                patterns = (
                    (msg.pattern,)
                    if isinstance(msg, PatternMessage)
                    else msg.variants.values()
                )
                if any(all(el == "" for el in pattern) for pattern in patterns):
                    errors.append("Empty translations are not allowed")
            except ValueError as e:
                msg = None
                errors.append(f"Parse error: {e}")

            if isinstance(msg, SelectMessage):
                try:
                    orig_msg = mf2_parse_message(original)
                except ValueError:
                    orig_msg = None
                if not isinstance(orig_msg, SelectMessage):
                    errors.append("Plural translation requires plural source")

            if entity.resource.format == Resource.Format.GETTEXT:
                # Bug 1599056: Original and translation must either both end in a newline,
                # or none of them should.
                if original.endswith("\n") != string.endswith("\n"):
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
