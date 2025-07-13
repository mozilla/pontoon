from collections import defaultdict

from fluent.syntax import FluentParser, ast
from fluent.syntax.visitor import Visitor
from moz.l10n.formats.mf2 import mf2_parse_message
from moz.l10n.model import PatternMessage


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


def run_checks(entity, original, string):
    """
    Group all checks related to the base UI that get stored in the DB
    :arg pontoon.base.models.Entity entity: Source entity
    :arg basestring original: an original string
    :arg basestring string: a translation
    """
    checks = defaultdict(list)
    format = entity.resource.format

    # Bug 1599056: Original and translation must either both end in a newline,
    # or none of them should.
    if format == "gettext":
        if original.endswith("\n") != string.endswith("\n"):
            checks["pErrors"].append("Ending newline mismatch")
        if string != "":
            try:
                msg = mf2_parse_message(string)
                patterns = (
                    (msg.pattern,)
                    if isinstance(msg, PatternMessage)
                    else msg.variants.values()
                )
                if any(not pattern or pattern == [""] for pattern in patterns):
                    checks["pErrors"].append("Empty translations are not allowed")
            except ValueError as e:
                checks["pErrors"].append(f"Parse error: {e}")

    # Prevent empty translation submissions if not supported
    if string == "" and not entity.resource.allows_empty_translations:
        checks["pErrors"].append("Empty translations are not allowed")

    # FTL checks
    if format == "fluent" and string != "":
        translation_ast = parser.parse_entry(string)
        entity_ast = parser.parse_entry(entity.string)

        # Parse error
        if isinstance(translation_ast, ast.Junk):
            checks["pErrors"].append(translation_ast.annotations[0].message)

        # Not a localizable entry
        elif not isinstance(translation_ast, (ast.Message, ast.Term)):
            checks["pErrors"].append(
                "Translation needs to be a valid localizable entry"
            )

        # Message ID mismatch
        elif entity_ast.id.name != translation_ast.id.name:
            checks["pErrors"].append("Translation key needs to match source string key")

        # Empty translation entry warning; set here rather than pontoon_non_db.py
        # to avoid needing to parse the Fluent message twice.
        else:
            visitor = IsEmptyVisitor()
            visitor.visit(translation_ast)
            if visitor.is_empty:
                checks["pndbWarnings"].append("Empty translation")

    return checks
