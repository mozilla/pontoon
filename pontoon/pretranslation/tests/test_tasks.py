from unittest.mock import patch

import pytest

from pontoon.base.models import ChangedEntityLocale, Translation, User
from pontoon.pretranslation.tasks import pretranslate
from pontoon.test.factories import (
    EntityFactory,
    ResourceFactory,
    TranslatedResourceFactory,
    TranslationFactory,
    ProjectLocaleFactory,
)


@patch("pontoon.pretranslation.tasks.get_pretranslations")
@pytest.mark.django_db
def test_pretranslate(gt_mock, project_a, locale_a, resource_a, locale_b):
    project_a.pretranslation_enabled = True
    project_a.save()

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
        project=project_a,
        locale=locale_a,
        pretranslation_enabled=True,
    )
    ProjectLocaleFactory.create(
        project=project_a,
        locale=locale_b,
        pretranslation_enabled=True,
    )

    gt_user = User.objects.get(email="pontoon-gt@example.com")
    gt_mock.return_value = [("pretranslation", None, gt_user)]

    pretranslate(project_a.pk)
    project_a.refresh_from_db()
    translations = Translation.objects.filter(user=gt_user)

    # Total pretranslations = 2(tr_ax) + 2(tr_bx) + 2(tr_ay)
    assert len(translations) == 6

    assert ChangedEntityLocale.objects.all().count() == 6

    # pretranslated count == total pretranslations.
    assert project_a.pretranslated_strings == 6

    # latest_translation belongs to pretranslations.
    assert project_a.latest_translation in translations


@patch("pontoon.pretranslation.tasks.get_pretranslations")
@pytest.mark.django_db
def test_which_strings_to_pretranslate(gt_mock, project_a, locale_a, resource_a):
    """
    Verify that we only pretranslate:
    - strings without any translations
    - strings with only rejected translations, submitted by humans
    """
    project_a.pretranslation_enabled = True
    project_a.save()

    ProjectLocaleFactory.create(
        project=project_a,
        locale=locale_a,
        pretranslation_enabled=True,
    )

    resource = ResourceFactory.create(
        project=project_a, path="resource.po", format="po"
    )
    TranslatedResourceFactory.create(resource=resource, locale=locale_a)

    no_translations = EntityFactory.create(resource=resource)
    non_rejected = EntityFactory.create(resource=resource)
    rejected_by_human = EntityFactory.create(resource=resource)
    rejected_by_machine = EntityFactory.create(resource=resource)

    gt_user = User.objects.get(email="pontoon-gt@example.com")
    gt_mock.return_value = [("pretranslation", None, gt_user)]

    TranslationFactory.create(entity=non_rejected, locale=locale_a, rejected=False)
    TranslationFactory.create(entity=rejected_by_human, locale=locale_a, rejected=True)
    TranslationFactory.create(
        entity=rejected_by_machine,
        locale=locale_a,
        rejected=True,
        user=gt_user,
    )

    pretranslate(project_a.pk)
    project_a.refresh_from_db()

    assert len(no_translations.translation_set.filter(string="pretranslation")) == 1
    assert len(non_rejected.translation_set.filter(string="pretranslation")) == 0
    assert len(rejected_by_human.translation_set.filter(string="pretranslation")) == 1
    assert len(rejected_by_machine.translation_set.filter(string="pretranslation")) == 0
