from __future__ import absolute_import

from mock import patch

import pytest

from pontoon.base.models import User, Translation
from pontoon.pretranslation.pretranslate import get_translations
from pontoon.pretranslation.tasks import pretranslate
from pontoon.test.factories import (
    EntityFactory,
    ResourceFactory,
    TranslationMemoryFactory,
    TranslatedResourceFactory,
    ProjectLocaleFactory,
)


@patch('pontoon.pretranslation.pretranslate.get_google_translate_data')
@pytest.mark.django_db
def test_pretranslation_get_translations(gt_mock, locale_b, resource_a, google_translate_locale):
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
            entity=entity,
            source=entity.string,
            target=entity.string,
            locale=locale_b,
        )
        TranslationMemoryFactory.create(
            entity=entity,
            source=entity.string,
            target=entity.string,
            locale=google_translate_locale,
        )
    # Mock the return value of get_google_translate_data
    gt_mock.return_value = {
        'status': True,
        'translation': entities[2].string,
    }

    tm_user = User.objects.get(email="pontoon-tm@mozilla.com")
    gt_user = User.objects.get(email="pontoon-gt@mozilla.com")

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
    assert response == [(entities[2].string, None, gt_user)]

    # Entity.string_plural is not None.
    response_a = get_translations(entities[1], google_translate_locale)
    response_b = get_translations(entities[3], google_translate_locale)
    assert response_b == [(entities[2].string, 0, gt_user), (entities[2].string, 1, gt_user)]
    assert response_a == [(entities[1].string, 0, tm_user), (entities[1].string, 1, tm_user)]


@patch('pontoon.pretranslation.tasks.get_translations')
@pytest.mark.django_db
def test_pretranslation_pretranslate(gt_mock, project_a, locale_a, resource_a, locale_b):
    resources = [
        ResourceFactory(project=project_a, path=x, format="po")
        for x in ["resource_x.po", "resource_y.po"]
    ]

    for i, x in enumerate(["abaa", "abac"]):
        EntityFactory.create(resource=resources[0], string=x, order=i)

    for i, x in enumerate(["aaab", "abab"]):
        EntityFactory.create(resource=resources[1], string=x, order=i)

    TranslatedResourceFactory.create(
        resource=resources[0], locale=locale_a
    )
    TranslatedResourceFactory.create(
        resource=resources[0], locale=locale_b
    )
    TranslatedResourceFactory.create(
        resource=resources[1], locale=locale_a
    )

    ProjectLocaleFactory.create(
        project=project_a,
        locale=locale_a,
    )
    ProjectLocaleFactory.create(
        project=project_a,
        locale=locale_b,
    )

    tm_user = User.objects.get(email="pontoon-tm@mozilla.com")
    gt_mock.return_value = [("pretranslation", None, tm_user)]

    pretranslate(project_a)

    translations = Translation.objects.filter(user=tm_user)

    # Total pretranslations = 2(tr_ax) + 2(tr_bx) + 2(tr_ay)
    assert len(translations) == 6

    # unreviewed count == total pretranslations.
    assert project_a.unreviewed_strings == 6

    # latest_translation belongs to pretranslations.
    assert project_a.latest_translation in translations
