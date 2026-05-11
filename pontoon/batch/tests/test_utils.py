from unittest.mock import MagicMock

import pytest

from fluent.syntax import FluentParser, FluentSerializer

from pontoon.base.models import Locale, Translation
from pontoon.batch.actions import copy_translation_from_locale
from pontoon.batch.utils import (
    find_and_replace,
    ftl_find_and_replace,
)
from pontoon.test.factories import (
    EntityFactory,
    ProjectFactory,
    ResourceFactory,
    TranslationFactory,
    UserFactory,
)


parser = FluentParser()
serializer = FluentSerializer()


def normalize(string):
    # Serialize strings using default Fluent serializer rules
    # to avoid differences caused by different formatting style.
    return serializer.serialize_entry(parser.parse_entry(string))


def test_ftl_find_and_replace():
    simple_string = normalize("key = find")
    simple_replaced = normalize("key = replace")

    assert ftl_find_and_replace(simple_string, "find", "replace") == simple_replaced

    # Perform find and replace on text values only
    complex_string = normalize(
        """find =
        .placeholder = find
    """
    )
    complex_replaced = normalize(
        """find =
        .placeholder = replace
    """
    )

    assert ftl_find_and_replace(complex_string, "find", "replace") == complex_replaced


@pytest.mark.django_db
def test_ftl_find_and_replace_non_text_value(locale_a, user_a):
    complex_string = normalize(
        """find =
        .placeholder = find
    """
    )

    project = ProjectFactory(slug="project", name="Project")
    resource = ResourceFactory(project=project, path="resource.ftl", format="fluent")
    entity = EntityFactory(resource=resource, string=complex_string)
    translation = TranslationFactory(
        entity=entity, locale=locale_a, string=complex_string
    )

    translations, translations_to_create, translations_with_errors = find_and_replace(
        Translation.objects.filter(pk__in=[translation.pk]),
        "placeholder",
        "replace",
        user_a,
    )

    assert len(translations) == 0
    assert translations_to_create == []
    assert translations_with_errors == []


@pytest.mark.django_db
def test_copy_from_similar_locale():
    """
    Translations that are approved in a similar locale can be copied to the current locale as suggestions.
    """

    project = ProjectFactory(slug="project", name="Project")
    resource = ResourceFactory(project=project, path="resource.ftl", format="fluent")
    entity = EntityFactory(resource=resource, string="key = value")
    target_locale = Locale.objects.get(code="en-ZA")
    user = UserFactory()

    source_locale = Locale.objects.get(code="en-GB")

    TranslationFactory(
        entity=entity, locale=source_locale, string="key = value", approved=True
    )

    # Mock form and call the function
    form = MagicMock()
    form.cleaned_data = {
        "other_locale": "en-GB",
        "entities": [entity.pk],
    }

    copy_translation_from_locale(form, user, Translation.objects.none(), target_locale)
    result = Translation.objects.filter(locale=target_locale, entity=entity)

    # Assert a suggestion was created in the target locale
    assert Translation.objects.filter(
        locale=target_locale,
        entity=entity,
        approved=False,
    ).exists()
    assert result.count() == 1
    assert not result.first().approved
    assert result.first().string == "key = value"
