from unittest.mock import patch

import pytest

from pontoon.actionlog.models import ActionLog
from pontoon.base.models import ChangedEntityLocale, Translation
from pontoon.checks.models import Error, Warning
from pontoon.pretranslation.tasks import pretranslate_task
from pontoon.test.factories import (
    EntityFactory,
    ProjectLocaleFactory,
    ResourceFactory,
    TranslatedResourceFactory,
    TranslationFactory,
)


@patch("pontoon.pretranslation.tasks.get_pretranslation")
@pytest.mark.django_db
def test_pretranslate(gt_mock, project_a, locale_a, resource_a, locale_b, gt_user):
    project_a.pretranslation_enabled = True
    project_a.save()

    resources = [
        ResourceFactory(project=project_a, path=x, format="gettext")
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

    gt_mock.return_value = ("pretranslation", "gt")

    pretranslate_task(project_a.pk)
    project_a.refresh_from_db()
    translations = Translation.objects.filter(user=gt_user)

    # Total pretranslations = 2(tr_ax) + 2(tr_bx) + 2(tr_ay)
    assert len(translations) == 6

    assert ChangedEntityLocale.objects.all().count() == 6

    # pretranslated count == total pretranslations.
    assert project_a.pretranslated_strings == 6

    # latest_translation belongs to pretranslations.
    assert project_a.latest_translation in translations


@patch("pontoon.pretranslation.tasks.get_pretranslation")
@pytest.mark.django_db
def test_which_strings_to_pretranslate(
    gt_mock, project_a, locale_a, resource_a, gt_user
):
    """
    Verify that we pretranslate strings without an approved translation, except:
    - strings with an existing pretranslation, by any author
    - strings whose pretranslation by a bot was rejected

    Skipped strings are not sent to machine translation.
    """
    project_a.pretranslation_enabled = True
    project_a.save()

    ProjectLocaleFactory.create(
        project=project_a,
        locale=locale_a,
        pretranslation_enabled=True,
    )

    resource = ResourceFactory.create(
        project=project_a, path="resource.po", format="gettext"
    )
    TranslatedResourceFactory.create(resource=resource, locale=locale_a)

    no_translations = EntityFactory.create(resource=resource)
    non_rejected = EntityFactory.create(resource=resource)
    rejected_by_human = EntityFactory.create(resource=resource)
    rejected_by_machine = EntityFactory.create(resource=resource)
    approved = EntityFactory.create(resource=resource)
    pretranslated_by_machine = EntityFactory.create(resource=resource)
    pretranslated_by_human = EntityFactory.create(resource=resource)

    gt_mock.return_value = ("pretranslation", "gt")

    TranslationFactory.create(entity=non_rejected, locale=locale_a, rejected=False)
    TranslationFactory.create(entity=rejected_by_human, locale=locale_a, rejected=True)
    TranslationFactory.create(
        entity=rejected_by_machine,
        locale=locale_a,
        rejected=True,
        user=gt_user,
    )
    TranslationFactory.create(
        entity=approved, locale=locale_a, approved=True, active=True
    )
    TranslationFactory.create(
        entity=pretranslated_by_machine,
        locale=locale_a,
        user=gt_user,
        pretranslated=True,
        active=True,
    )
    # A converted suggestion, or a pretranslation uploaded through the API
    TranslationFactory.create(
        entity=pretranslated_by_human, locale=locale_a, pretranslated=True, active=True
    )

    pretranslate_task(project_a.pk)
    project_a.refresh_from_db()

    assert len(no_translations.translation_set.filter(string="pretranslation")) == 1
    assert len(non_rejected.translation_set.filter(string="pretranslation")) == 1
    assert len(rejected_by_human.translation_set.filter(string="pretranslation")) == 1
    assert len(rejected_by_machine.translation_set.filter(string="pretranslation")) == 0
    assert len(approved.translation_set.filter(string="pretranslation")) == 0
    assert (
        len(pretranslated_by_machine.translation_set.filter(string="pretranslation"))
        == 0
    )
    assert (
        len(pretranslated_by_human.translation_set.filter(string="pretranslation")) == 0
    )

    assert {call.args[0] for call in gt_mock.call_args_list} == {
        no_translations,
        non_rejected,
        rejected_by_human,
    }


@patch("pontoon.pretranslation.tasks.run_checks")
@patch("pontoon.pretranslation.tasks.get_pretranslation")
@pytest.mark.django_db
def test_pretranslate_skips_unparsable_pretranslation(
    gt_mock, checks_mock, project_a, locale_a, gt_user, caplog
):
    """
    An entity whose pretranslation doesn't parse must not abort the pretranslation
    of other entities.
    """
    project_a.pretranslation_enabled = True
    project_a.save()

    resource = ResourceFactory.create(
        project=project_a, path="resource.ftl", format="fluent"
    )
    TranslatedResourceFactory.create(resource=resource, locale=locale_a)
    ProjectLocaleFactory.create(
        project=project_a,
        locale=locale_a,
        pretranslation_enabled=True,
    )

    EntityFactory.create(resource=resource, string="key-a = A\n", order=0)
    EntityFactory.create(resource=resource, string="key-b = B\n", order=1)

    checks_mock.return_value = {}
    gt_mock.side_effect = [
        ("key-a = unescaped { brace\n", "gt"),
        ("key-b = GT\n", "gt"),
    ]

    with caplog.at_level("ERROR", logger="pontoon.pretranslation.tasks"):
        pretranslate_task(project_a.pk)

    assert "Unparsable pretranslation" in caplog.text
    assert [t.string for t in Translation.objects.filter(user=gt_user)] == [
        "key-b = GT\n"
    ]


@pytest.fixture
def po_resource(project_a, locale_a):
    """A gettext resource of a project with pretranslation enabled for locale_a."""
    project_a.pretranslation_enabled = True
    project_a.save()
    ProjectLocaleFactory.create(
        project=project_a, locale=locale_a, pretranslation_enabled=True
    )
    resource = ResourceFactory.create(
        project=project_a, path="resource.po", format="gettext"
    )
    TranslatedResourceFactory.create(resource=resource, locale=locale_a)
    return resource


@patch("pontoon.pretranslation.tasks.run_checks", return_value={})
@patch("pontoon.pretranslation.tasks.get_pretranslation")
@pytest.mark.django_db
def test_pretranslate_keeps_other_suggestions(
    gt_mock, checks_mock, project_a, locale_a, po_resource, gt_user
):
    """Suggestions that don't match the pretranslation are kept as suggestions."""
    entity = EntityFactory.create(resource=po_resource)
    suggestion = TranslationFactory.create(entity=entity, locale=locale_a, active=True)
    gt_mock.return_value = ("pretranslation", "gt")

    pretranslate_task(project_a.pk)

    suggestion.refresh_from_db()
    assert not suggestion.rejected
    assert not suggestion.pretranslated
    assert not suggestion.active

    pretranslation = Translation.objects.get(entity=entity, string="pretranslation")
    assert pretranslation.pretranslated
    assert pretranslation.active
    assert pretranslation.user == gt_user


@patch("pontoon.pretranslation.tasks.run_checks", return_value={})
@patch("pontoon.pretranslation.tasks.get_pretranslation")
@pytest.mark.django_db
def test_pretranslate_replaces_fuzzy(
    gt_mock, checks_mock, project_a, locale_a, po_resource, gt_user, tm_user
):
    """
    A different fuzzy translation is rejected and replaced. The rejection is
    recorded as done by the bot that produced the pretranslation.
    """
    by_gt = EntityFactory.create(resource=po_resource)
    by_tm = EntityFactory.create(resource=po_resource)
    fuzzy_gt = TranslationFactory.create(
        entity=by_gt, locale=locale_a, fuzzy=True, active=True
    )
    fuzzy_tm = TranslationFactory.create(
        entity=by_tm, locale=locale_a, fuzzy=True, active=True
    )
    gt_mock.side_effect = lambda entity, locale, **kwargs: {
        by_gt.pk: ("pretranslation", "gt"),
        by_tm.pk: ("pretranslation", "tm"),
    }[entity.pk]

    pretranslate_task(project_a.pk)

    for fuzzy, bot in [(fuzzy_gt, gt_user), (fuzzy_tm, tm_user)]:
        fuzzy.refresh_from_db()
        assert fuzzy.rejected
        assert not fuzzy.fuzzy
        assert not fuzzy.active
        assert fuzzy.rejected_user == bot

        log = ActionLog.objects.get(
            translation=fuzzy, action_type=ActionLog.ActionType.TRANSLATION_REJECTED
        )
        assert log.performed_by == bot

        pretranslation = Translation.objects.get(
            entity=fuzzy.entity, string="pretranslation"
        )
        assert pretranslation.active
        assert pretranslation.user == bot


@patch("pontoon.pretranslation.tasks.run_checks", return_value={})
@patch("pontoon.pretranslation.tasks.get_pretranslation")
@pytest.mark.django_db
def test_pretranslate_converts_matching_suggestion(
    gt_mock, checks_mock, project_a, locale_a, po_resource, tm_user
):
    """
    A suggestion matching the pretranslation becomes the pretranslation, keeping its
    author and losing the checks stored for it. A fuzzy translation is still
    rejected, as done by the bot.
    """
    entity = EntityFactory.create(resource=po_resource)
    suggestion = TranslationFactory.create(
        entity=entity,
        locale=locale_a,
        string="pretranslation",
        value=["pretranslation"],
    )
    author = suggestion.user
    Warning.objects.create(library="p", message="Stale warning", translation=suggestion)
    Error.objects.create(library="p", message="Stale error", translation=suggestion)
    fuzzy = TranslationFactory.create(
        entity=entity, locale=locale_a, fuzzy=True, active=True
    )
    gt_mock.return_value = ("pretranslation", "tm")

    pretranslate_task(project_a.pk)

    # No translation was created.
    assert Translation.objects.filter(entity=entity).count() == 2

    suggestion.refresh_from_db()
    assert suggestion.pretranslated
    assert suggestion.active
    assert not suggestion.approved
    assert suggestion.user == author
    assert not suggestion.warnings.exists()
    assert not suggestion.errors.exists()

    fuzzy.refresh_from_db()
    assert fuzzy.rejected
    assert fuzzy.rejected_user == tm_user


@patch("pontoon.pretranslation.tasks.run_checks")
@patch("pontoon.pretranslation.tasks.get_pretranslation")
@pytest.mark.django_db
def test_pretranslate_skips_pretranslation_failing_checks(
    gt_mock, checks_mock, project_a, locale_a, po_resource, gt_user
):
    """
    A pretranslation failing checks is retried with placeables preserved, and is not
    stored if the retry fails checks as well.
    """
    fixed_by_retry = EntityFactory.create(resource=po_resource)
    still_failing = EntityFactory.create(resource=po_resource)

    def pretranslation(entity, locale, preserve_placeables=False):
        if entity == fixed_by_retry and preserve_placeables:
            return ("passes checks", "gt")
        return ("fails checks", "gt")

    gt_mock.side_effect = pretranslation
    checks_mock.side_effect = lambda entity, locale_code, string, **kwargs: (
        {"pErrors": ["Failed check"]} if string == "fails checks" else {}
    )

    pretranslate_task(project_a.pk)

    gt_mock.assert_any_call(still_failing, locale_a, preserve_placeables=True)
    assert [t.string for t in Translation.objects.filter(user=gt_user)] == [
        "passes checks"
    ]


@patch("pontoon.pretranslation.tasks.run_checks", return_value={})
@patch("pontoon.pretranslation.tasks.get_pretranslation")
@pytest.mark.django_db
def test_pretranslate_skips_strings_changed_concurrently(
    gt_mock, checks_mock, project_a, locale_a, po_resource, admin
):
    """
    A string whose translations change while pretranslating is left out, as its
    pretranslation was decided on a state that no longer exists.
    """
    approved_meanwhile = EntityFactory.create(resource=po_resource)
    suggestion = TranslationFactory.create(
        entity=approved_meanwhile, locale=locale_a, active=True
    )
    translated_meanwhile = EntityFactory.create(resource=po_resource)
    unchanged = EntityFactory.create(resource=po_resource)

    def review_during_machine_translation(entity, locale, **kwargs):
        # The first call runs after the translations of all strings were read.
        if gt_mock.call_count == 1:
            suggestion.approve(admin)
            TranslationFactory.create(
                entity=translated_meanwhile, locale=locale_a, approved=True, active=True
            )
        return ("pretranslation", "gt")

    gt_mock.side_effect = review_during_machine_translation

    pretranslate_task(project_a.pk)

    pretranslated = Translation.objects.filter(string="pretranslation")
    assert [t.entity for t in pretranslated] == [unchanged]

    suggestion.refresh_from_db()
    assert suggestion.approved
    assert suggestion.active