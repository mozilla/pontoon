from fluent.syntax.visitor import Transformer

from pontoon.base.fluent import create_locale_plural_variants, flatten_pattern_elements


class PretranslationTransformer(Transformer):
    """
    Flattens the given Pattern, uplifting selectors to the highest possible level and
    duplicating shared parts in the variants. All other Placeables are serialised as
    TextElements.
    """

    def __init__(self, locale, callback):
        self.services = []
        self.locale = locale
        self.callback = callback

    def visit_Attribute(self, node):
        flatten_pattern_elements(node.value)
        return self.generic_visit(node)

    def visit_Message(self, node):
        if node.value:
            flatten_pattern_elements(node.value)
        return self.generic_visit(node)

    def visit_SelectExpression(self, node):
        create_locale_plural_variants(node, self.locale)
        return self.generic_visit(node)

    def visit_TextElement(self, node):
        pretranslation, service = self.callback(node.value, self.locale)

        if pretranslation is None:
            raise ValueError(
                f"Pretranslation for `{node.value}` to {self.locale.code} not available."
            )

        node.value = pretranslation
        self.services.append(service)
        return node
