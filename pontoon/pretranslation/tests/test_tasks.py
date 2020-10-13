from mock import patch

import pytest

from pontoon.base.models import User, Translation
from pontoon.pretranslation.tasks import pretranslate
from pontoon.test.factories import (
    EntityFactory,
    ResourceFactory,
    TranslatedResourceFactory,
    ProjectLocaleFactory,
)


@patch("pontoon.pretranslation.tasks.get_translations")
@pytest.mark.django_db
def test_pretranslate(gt_mock, project_a, locale_a, resource_a, locale_b):
    resources = [
        ResourceFactory(project=project_a, path=x, format="po")
        for x in ["resource_x.po", "resource_y.po"]
    ]

    for i, x in enumerate(["abaa", "abac"]):
        EntityFactory.create(resource=resources[0], string=x, order=i)

    for i, x in enumerate(["aaab", "abab"]):
        EntityFactory.create(resource=resources[1], string=x, order=i)

    TranslatedResourceFactory.create(resource=resources[0], locale=locale_a)
    TranslatedResourceFactory.create(resource=resources[0], locale=locale_b)
    TranslatedResourceFactory.create(resource=resources[1], locale=locale_a)

    ProjectLocaleFactory.create(
        project=project_a, locale=locale_a,
    )
    ProjectLocaleFactory.create(
        project=project_a, locale=locale_b,
    )

    tm_user = User.objects.get(email="pontoon-tm@example.com")
    gt_mock.return_value = [("pretranslation", None, tm_user)]

    pretranslate(project_a.pk)
    project_a.refresh_from_db()
    translations = Translation.objects.filter(user=tm_user)

    # Total pretranslations = 2(tr_ax) + 2(tr_bx) + 2(tr_ay)
    assert len(translations) == 6

    # fuzzy count == total pretranslations.
    assert project_a.fuzzy_strings == 6

    # latest_translation belongs to pretranslations.
    assert project_a.latest_translation in translations
