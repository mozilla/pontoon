import logging
import operator
import re

from django.db.models import CharField, Value as V
from django.db.models.functions import Concat

from fluent.syntax import FluentParser, FluentSerializer
from functools import reduce

from pontoon.base.models import User, TranslatedResource
from pontoon.base.fluent import FlatTransformer, create_locale_plural_variants
from pontoon.machinery.utils import (
    get_google_translate_data,
    get_translation_memory_data,
)


log = logging.getLogger(__name__)

parser = FluentParser()
serializer = FluentSerializer()


class PretranslationTransformer(FlatTransformer):
    def __init__(self, locale):
        self.services = []
        self.locale = locale

    def visit_SelectExpression(self, node):
        create_locale_plural_variants(node, self.locale)
        return self.generic_visit(node)

    def visit_TextElement(self, node):
        pretranslation, service = get_pretranslated_data(node.value, self.locale)

        if pretranslation is None:
            raise ValueError(
                f"Pretranslation for `{node.value}` to {self.locale.code} not available."
            )

        node.value = pretranslation
        self.services.append(service)
        return node


def get_pretranslations(entity, locale):
    """
    Get pretranslations for the entity-locale pair using internal translation memory and
    Google's machine translation.

    For Fluent strings, uplift SelectExpressions, serialize Placeables as TextElements
    and then only pretranslate TextElements. Set the most frequent TextElement
    pretranslation author as the author of the entire pretranslation.

    :arg Entity entity: the Entity object
    :arg Locale locale: the Locale object

    :returns: a list of tuples, consisting of:
        - a pretranslation of the entity
        - a plural form
        - a user (representing TM or GT service)
    """
    source = entity.string
    services = {
        "tm": User.objects.get(email="pontoon-tm@example.com"),
        "gt": User.objects.get(email="pontoon-gt@example.com"),
    }

    if entity.resource.format == "ftl":
        source_ast = parser.parse_entry(source)
        pt_transformer = PretranslationTransformer(locale)

        try:
            pretranslated_ast = pt_transformer.visit(source_ast)
        except ValueError as e:
            log.info(f"Fluent pretranslation error: {e}")
            return []

        pretranslation = serializer.serialize_entry(pretranslated_ast)

        authors = [services[service] for service in pt_transformer.services]
        author = max(set(authors), key=authors.count) if authors else services["tm"]

        return [(pretranslation, None, author)]

    else:
        pretranslation, service = get_pretranslated_data(source, locale)

        if pretranslation is None:
            return []

        author = services[service]
        if entity.string_plural == "":
            return [(pretranslation, None, author)]
        else:
            plural_forms = range(0, locale.nplurals or 1)
            return [
                (pretranslation, plural_form, author) for plural_form in plural_forms
            ]


def get_pretranslated_data(source, locale):
    # Empty strings do not need translation
    if re.search("^\\s*$", source):
        return source, "tm"

    # Try to get matches from Translation Memory
    tm_response = get_translation_memory_data(text=source, locale=locale)
    tm_perfect = [t for t in tm_response if int(t["quality"]) == 100]
    if tm_perfect:
        return tm_perfect[0]["target"], "tm"

    # Fetch from Google Translate
    elif locale.google_translate_code:
        gt_response = get_google_translate_data(text=source, locale=locale)
        if gt_response["status"]:
            return gt_response["translation"], "gt"

    return None, None


def update_changed_instances(tr_filter, tr_dict, translations):
    """
    Update the latest activity and stats for changed Locales, ProjectLocales
    & TranslatedResources
    """
    tr_filter = tuple(tr_filter)
    # Combine all generated filters with an OK operator.
    # `operator.ior` is the '|' Python operator, which turns into a logical OR
    # when used between django ORM query objects.
    tr_query = reduce(operator.ior, tr_filter)

    translatedresources = TranslatedResource.objects.filter(tr_query).annotate(
        locale_resource=Concat(
            "locale_id", V("-"), "resource_id", output_field=CharField()
        )
    )

    translatedresources.update_stats()

    for tr in translatedresources:
        index = tr_dict[tr.locale_resource]
        translation = translations[index]
        translation.update_latest_translation()
