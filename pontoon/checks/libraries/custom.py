from collections import Counter
from collections.abc import Iterable, Iterator
from re import DOTALL, compile, escape, fullmatch, search
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
    Group all checks related to the base UI
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
    non_db_warnings: list[str] = []
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

                require_placeholders_match(format, orig_msg, msg, errors, warnings)

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

            # Empty translation entry warning; set here rather than with the other
            # non-DB warnings to avoid needing to parse the Fluent message twice.
            else:
                visitor = IsEmptyVisitor()
                visitor.visit(translation_ast)
                if visitor.is_empty:
                    non_db_warnings.append("Empty translation")

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
        checks["pWarnings"] = warnings
    if non_db_warnings:
        checks["pndbWarnings"] = non_db_warnings
    return checks


printf_re = compile(
    r"%#@\w+@|%(?:[1-9][0-9]*\$|<)?[-#+ 0,(]?[0-9.]*(?:hh?|ll?|[qztjLT])?.?"
)
# Match whole HTML tags, but count printf placeholders inside their attributes too.
ph_re = compile(r"<[^>]+>|" + printf_re.pattern)

tag_re = compile(r"<\s*(/?)\s*([A-Za-z_][\w:.-]*)(.*?)(/?)\s*>", DOTALL)


def is_element(tag: str, context: str) -> bool:
    """
    Tell markup apart from literal text such as "Press <Enter> to continue".

    Strings read from a resource file are well-formed XML, so markup there always
    carries attributes, is self-closing, or has its counterpart in the same pattern.
    A bare angle-bracketed word can only have been escaped literal text.
    """
    tm = fullmatch(tag_re, tag)
    if tm is None:
        return False
    closing, name, attributes, self_closing = tm.groups()
    if self_closing or attributes.strip():
        return True
    pair = (
        rf"<\s*{escape(name)}\s*(?:/?>|\s)" if closing else rf"</\s*{escape(name)}\s*>"
    )
    return search(pair, context) is not None


def mismatched_tags(preview: str) -> set[tuple[int, int]]:
    """
    Find spans of tags whose nesting doesn't line up, as in "<a>text</b>".
    """
    open_tags: list[tuple[str, tuple[int, int]]] = []
    mismatched: set[tuple[int, int]] = set()
    for pm in ph_re.finditer(preview):
        tm = fullmatch(tag_re, pm[0]) if pm[0].startswith("<") else None
        if tm is None:
            continue
        closing, name, _, self_closing = tm.groups()
        if self_closing:
            continue
        if not closing:
            open_tags.append((name, pm.span()))
        elif open_tags and open_tags[-1][0] == name:
            open_tags.pop()
        else:
            # Unclosed tags on their own are ambiguous, so only a mismatch
            # between start and end counts.
            mismatched.add(pm.span())
            if open_tags:
                mismatched.add(open_tags.pop()[1])
    return mismatched


def count_unnumbered_placeholders(preview: str) -> Counter[str]:
    return Counter(
        pm[0]
        for pm in printf_re.finditer(preview)
        if pm[0] not in {"%%", "%n"}
        and not fullmatch(r"%(?:[1-9][0-9]*\$|<|#@).*", pm[0])
    )


def require_placeholders_match(
    format: Resource.Format,
    src: Message | None,
    tgt: Message,
    errors: list[str],
    warnings: list[str],
) -> None:
    src_ph_strings: set[str] = set()
    required_ph: set[str] = set()
    src_min_counts: Counter[str] | None = None
    src_max_counts: Counter[str] = Counter()
    source_elements: list[Counter[str]] = []
    if src:
        for pattern in get_patterns(src):
            preview = ""
            ph_spans: list[tuple[int, int, str]] = []
            for el in pattern:
                if isinstance(el, str):
                    if "%" in el:
                        # Assume a source with a literal % doesn't use printf formatting.
                        return
                    preview += el
                    continue
                ps = preview_placeholder(el)
                if not (
                    isinstance(el, Expression)
                    and isinstance(el.arg, str)
                    and el.function in (None, "html")
                ):
                    src_ph_strings.add(ps)
                    ph_spans.append((len(preview), len(preview) + len(ps), ps))
                preview += ps
            enclosed_spans: set[tuple[int, int, str]] = set()
            elements: Counter[str] = Counter()
            src_mismatched = mismatched_tags(preview)
            # Put tags back together when placeholders split them into parts.
            for pm in ph_re.finditer(preview):
                if pm[0].startswith("<") and (
                    is_element(pm[0], preview) or pm.span() in src_mismatched
                ):
                    src_ph_strings.add(pm[0])
                    required_ph.add(pm[0])
                    elements[pm[0]] += 1
                    enclosed_spans.update(
                        (start, end, ps)
                        for start, end, ps in ph_spans
                        if pm.start() <= start
                        and end <= pm.end()
                        and pm.span() != (start, end)
                    )
            required_ph.update(
                ps
                for start, end, ps in ph_spans
                if (start, end, ps) not in enclosed_spans
            )
            variant_counts = count_unnumbered_placeholders(preview)
            src_max_counts |= variant_counts
            src_min_counts = (
                variant_counts
                if src_min_counts is None
                else src_min_counts & variant_counts
            )
            source_elements.append(elements)
    if src_min_counts is None:
        src_min_counts = Counter()

    found_ph: set[str] = set()
    target_counts: list[Counter[str]] = []
    for pattern in get_patterns(tgt):
        pat_src = get_simple_preview(format, pattern)
        target_counts.append(count_unnumbered_placeholders(pat_src))
        tgt_mismatched = mismatched_tags(pat_src)

        for pm in ph_re.finditer(pat_src):
            for ph in src_ph_strings:
                if pat_src.startswith(ph, pm.start()):
                    found_ph.add(ph)
                    break
            else:
                ph = pm[0]
                if ph.startswith("<"):
                    if is_element(ph, pat_src) or pm.span() in tgt_mismatched:
                        errors.append(f"Element {ph} not found in reference")
                elif ph not in {"%%", "%n"}:
                    errors.append(f"Placeholder {ph} not found in reference")

    for ph in sorted(required_ph):
        if ph not in found_ph:
            kind = "Element" if ph.startswith("<") else "Placeholder"
            warnings.append(f"{kind} {ph} not found in translation")

    # Avoid a second warning for placeholders missing along with their tags.
    # Compare placeholder counts across source variants, since their tags may differ.
    missing_element_counts: Counter[str] | None = None
    for elements in source_elements:
        missing: Counter[str] = Counter()
        for element, count in elements.items():
            if element in required_ph and element not in found_ph:
                for ph, occurrences in count_unnumbered_placeholders(element).items():
                    missing[ph] += count * occurrences
        missing_element_counts = (
            missing
            if missing_element_counts is None
            else missing_element_counts & missing
        )
    if missing_element_counts is None:
        missing_element_counts = Counter()

    # Locales have different plural forms; each can use any count in the source range.
    for counts in target_counts:
        for ph, maximum in src_max_counts.items():
            minimum = src_min_counts[ph]
            found = counts[ph]
            if found > maximum:
                error = (
                    f"Placeholder {ph} has more occurrences in translation "
                    f"(expected {maximum}, found {found})"
                )
                if error not in errors:
                    errors.append(error)
            elif found + missing_element_counts[ph] < minimum:
                if ph in required_ph and ph not in found_ph:
                    # We already warned that this placeholder is missing.
                    continue
                warning = (
                    f"Placeholder {ph} has fewer occurrences in translation "
                    f"(expected {minimum}, found {found})"
                )
                if warning not in warnings:
                    warnings.append(warning)


def get_patterns(msg: Message) -> Iterable[Pattern]:
    return (msg.pattern,) if isinstance(msg, PatternMessage) else msg.variants.values()


def get_placeholders(patterns: Iterable[Pattern]) -> Iterator[Expression | Markup]:
    return (el for pattern in patterns for el in pattern if not isinstance(el, str))
