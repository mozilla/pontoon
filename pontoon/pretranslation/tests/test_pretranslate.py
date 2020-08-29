from __future__ import absolute_import

from mock import patch

import pytest

from pontoon.base.models import User
from pontoon.pretranslation.pretranslate import get_translations
from pontoon.test.factories import (
    EntityFactory,
    TranslationMemoryFactory,
)


@patch("pontoon.pretranslation.pretranslate.get_google_translate_data")
@pytest.mark.django_db
def test_get_translations(gt_mock, locale_b, resource_a, google_translate_locale):
    entities = [
        EntityFactory(resource=resource_a, string=x, order=i)
        for i, x in enumerate(["abaa", "abac", "aaab", "abab"])
    ]

    entities[1].string_plural = entities[1].string
    entities[3].string_plural = entities[3].string
    entities[1].save()
    entities[3].save()

    google_translate_locale.cldr_plurals = "1, 2"
    google_translate_locale.save()

    for entity in entities[0:2]:
        TranslationMemoryFactory.create(
            entity=entity, source=entity.string, target=entity.string, locale=locale_b,
        )
        TranslationMemoryFactory.create(
            entity=entity,
            source=entity.string,
            target=entity.string,
            locale=google_translate_locale,
        )

    # Mock the return value of get_google_translate_data
    gt_mock.return_value = {
        "status": True,
        "translation": "gt_translation",
    }

    tm_user = User.objects.get(email="pontoon-tm@example.com")
    gt_user = User.objects.get(email="pontoon-gt@example.com")

    # 100% match exists in translation memory.
    response_a = get_translations(entities[0], locale_b)
    response_b = get_translations(entities[0], google_translate_locale)
    assert response_a == [(entities[0].string, None, tm_user)]
    assert response_b == [(entities[0].string, None, tm_user)]

    # 100% match does not exists and locale.google_translate_code is None.
    response = get_translations(entities[2], locale_b)
    assert response == []

    # 100% match does not exists and locale.google_translate_code is not None.
    response = get_translations(entities[2], google_translate_locale)
    assert response == [("gt_translation", None, gt_user)]

    # Entity.string_plural is not None.
    response_a = get_translations(entities[1], google_translate_locale)
    response_b = get_translations(entities[3], google_translate_locale)
    assert response_a == [
        (entities[1].string, 0, tm_user),
        (entities[1].string, 1, tm_user),
    ]
    assert response_b == [
        ("gt_translation", 0, gt_user),
        ("gt_translation", 1, gt_user),
    ]
