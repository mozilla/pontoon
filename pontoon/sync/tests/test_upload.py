from datetime import timedelta
from types import SimpleNamespace

import pytest

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection, transaction
from django.test.utils import CaptureQueriesContext

from pontoon.actionlog.models import ActionLog
from pontoon.base.models import (
    ChangedEntityLocale,
    Resource,
    TranslatedResource,
    Translation,
)
from pontoon.checks.models import Error, Warning
from pontoon.sync import upload as sync_upload
from pontoon.sync.upload import (
    FailedCheck,
    UploadConflictError,
    UploadError,
    import_uploaded_file,
    import_uploaded_pretranslations,
    import_uploaded_suggestions,
)
from pontoon.test.factories import (
    EntityFactory,
    ResourceFactory,
    TranslatedResourceFactory,
    TranslationFactory,
)


PO_CONTENTS = 'msgid "test_key"\nmsgstr "new translation"'


def _po_file(contents=PO_CONTENTS, name="resource_a.po"):
    return SimpleUploadedFile(name, contents.encode("utf-8"))


def _import(
    importer, project_locale, resource, user, contents=PO_CONTENTS, upload=None
):
    return importer(
        project_locale.project,
        project_locale.locale,
        resource,
        upload or _po_file(contents),
        user,
    )


def _import_conflicts(importer, project_locale, resource, user):
    """Run an import that must fail on a conflict, rolling it back like the API does."""
    with pytest.raises(UploadConflictError), transaction.atomic():
        _import(importer, project_locale, resource, user)


@pytest.fixture
def uploader(user_b):
    """The user importing the file, distinct from the author of `po_translation`."""
    return user_b


@pytest.fixture
def po_translation(translation_a):
    """An unreviewed suggestion for `test_key`, in a gettext resource."""
    translation_a.entity.key = ["test_key"]
    translation_a.entity.save()
    return translation_a


@pytest.fixture
def resource(po_translation):
    return po_translation.entity.resource


@pytest.fixture
def untranslated_entity(po_translation):
    """An entity without translations, in the same resource as `po_translation`."""
    return EntityFactory.create(
        resource=po_translation.entity.resource,
        string="Other entity",
        key=["other_key"],
    )


@pytest.fixture
def android_entity(project_locale_a):
    """An entity with a placeholder, in an Android resource enabled for the locale."""
    resource = ResourceFactory.create(
        project=project_locale_a.project,
        path="values/strings.xml",
        format=Resource.Format.ANDROID,
    )
    TranslatedResourceFactory.create(resource=resource, locale=project_locale_a.locale)
    return EntityFactory.create(
        resource=resource, string="The page at {$arg1} says:", key=["page_at"]
    )


def _android_upload_without_placeholder():
    return SimpleUploadedFile(
        "strings.xml",
        b'<?xml version="1.0" encoding="utf-8"?>\n'
        b"<resources>\n"
        b'  <string name="page_at">La pagina sul server riporta:</string>\n'
        b"</resources>\n",
    )


def _failing_checks(results):
    """A `run_checks()` stand-in reporting `results` for the uploaded translation only."""

    def run_checks(entity, locale_code, string, use_tt_checks):
        return results if string == "new translation" else {}

    return run_checks


def _review_during_import(monkeypatch, review):
    """Call `review` from inside a running import.

    The importers call `timezone.now()` after reading the current translations and
    before writing anything, so this reproduces a review landing in the window the
    conflict check guards. It runs in the same transaction, so it does not exercise
    the locks themselves.
    """
    real_now = sync_upload.timezone.now
    reviewed = False

    def now_and_review():
        nonlocal reviewed
        if not reviewed:
            reviewed = True
            review()
        return real_now()

    monkeypatch.setattr(
        sync_upload, "timezone", SimpleNamespace(now=now_and_review), raising=False
    )


def _approve_during_import(monkeypatch, translation, user):
    _review_during_import(monkeypatch, lambda: translation.approve(user))


# Translations


@pytest.mark.django_db
def test_upload_translations_file(project_locale_a, resource, po_translation, uploader):
    result = _import(import_uploaded_file, project_locale_a, resource, uploader)

    assert result.updated == 1
    assert result.unchanged == 0
    assert result.undefined_keys == []

    translation = Translation.objects.get(string="new translation")

    assert translation.entity.key == ["test_key"]
    assert translation.approved
    assert translation.user == uploader
    assert not translation.warnings.exists()
    assert ActionLog.objects.filter(
        performed_by=uploader,
        action_type=ActionLog.ActionType.TRANSLATION_CREATED,
        translation=translation,
    ).exists()


@pytest.mark.django_db
def test_upload_translations_unchanged(
    project_locale_a, resource, po_translation, uploader
):
    """Re-importing a file that changed nothing is reported as unchanged."""
    first = _import(import_uploaded_file, project_locale_a, resource, uploader)
    assert first.updated == 1

    second = _import(import_uploaded_file, project_locale_a, resource, uploader)

    assert second.updated == 0
    assert second.unchanged == 1
    assert Translation.objects.filter(string="new translation").count() == 1


@pytest.mark.django_db
def test_upload_translations_unknown_keys_ignored(
    project_locale_a, resource, po_translation, uploader
):
    """Skip unknown keys and report them, importing the rest of the file."""
    result = _import(
        import_uploaded_file,
        project_locale_a,
        resource,
        uploader,
        contents='msgid "test_key"\nmsgstr "new translation"\n\n'
        'msgid "no_such_key"\nmsgstr "x"\n\n'
        'msgid "another_missing"\nmsgstr "y"\n',
    )

    assert result.updated == 1
    assert result.undefined_keys == [("no_such_key",), ("another_missing",)]
    assert result.undefined == 2
    assert Translation.objects.filter(string="new translation").exists()


@pytest.mark.django_db
def test_upload_translations_unparseable_file(
    project_locale_a, resource, po_translation, uploader
):
    with pytest.raises(UploadError, match="Could not parse uploaded file"):
        _import(
            import_uploaded_file,
            project_locale_a,
            resource,
            uploader,
            contents="this is not valid gettext {{{ broken",
        )


@pytest.mark.django_db
def test_upload_translations_file_without_translations(
    project_locale_a, resource, po_translation, uploader
):
    """A file with no translations is an error, rather than a no-op."""
    with pytest.raises(UploadError, match="No translations found"):
        _import(
            import_uploaded_file,
            project_locale_a,
            resource,
            uploader,
            contents="# Just a comment\n",
        )


# Pretranslations


@pytest.mark.django_db
def test_upload_pretranslations_creates_pretranslation(
    project_locale_a, resource, untranslated_entity, uploader
):
    """An untranslated string gets a new pretranslation, authored by the uploader."""
    result = _import(
        import_uploaded_pretranslations,
        project_locale_a,
        resource,
        uploader,
        contents='msgid "other_key"\nmsgstr "pretranslation"',
    )

    assert result.created == 1
    assert result.replaced == 0
    assert result.converted == 0
    assert result.unchanged == 0
    assert result.skipped == 0
    assert result.failed_checks == []
    assert result.undefined_keys == []

    translation = Translation.objects.get(entity=untranslated_entity)

    assert translation.string == "pretranslation"
    assert translation.pretranslated
    assert translation.active
    assert not translation.approved
    assert translation.user == uploader
    assert ActionLog.objects.filter(
        performed_by=uploader,
        action_type=ActionLog.ActionType.TRANSLATION_CREATED,
        translation=translation,
    ).exists()


@pytest.mark.django_db
def test_upload_pretranslations_skips_fuzzy_uploads(
    project_locale_a, resource, untranslated_entity, uploader
):
    """A translation marked as fuzzy in the file is not stored as a pretranslation."""
    result = _import(
        import_uploaded_pretranslations,
        project_locale_a,
        resource,
        uploader,
        contents='#, fuzzy\nmsgid "other_key"\nmsgstr "pretranslation"',
    )

    assert result.created == 0
    assert result.skipped == 1
    assert not Translation.objects.filter(entity=untranslated_entity).exists()


@pytest.mark.django_db
def test_upload_pretranslations_fuzzy_upload_keeps_existing_pretranslation(
    project_locale_a, resource, po_translation, uploader
):
    """A fuzzy entry leaves a different, existing pretranslation in place."""
    po_translation.approved = False
    po_translation.pretranslated = True
    po_translation.active = True
    po_translation.save()

    result = _import(
        import_uploaded_pretranslations,
        project_locale_a,
        resource,
        uploader,
        contents='#, fuzzy\nmsgid "test_key"\nmsgstr "fuzzy translation"',
    )

    assert result.skipped == 1

    po_translation.refresh_from_db()

    assert po_translation.pretranslated
    assert not po_translation.rejected
    assert po_translation.active
    assert Translation.objects.filter(entity=po_translation.entity).count() == 1


@pytest.mark.django_db
def test_upload_pretranslations_drops_replacement_with_errors(
    monkeypatch, project_locale_a, resource, po_translation, uploader
):
    """A replacement that fails checks is not stored, keeping the previous translation."""
    monkeypatch.setattr(
        sync_upload,
        "run_checks",
        _failing_checks({"pErrors": ["Test error", "Other error"]}),
    )
    po_translation.pretranslated = True
    po_translation.active = True
    po_translation.save()
    ChangedEntityLocale.objects.all().delete()

    result = _import(
        import_uploaded_pretranslations, project_locale_a, resource, uploader
    )

    assert result.replaced == 0
    assert result.failed_checks == [
        FailedCheck(
            key=("test_key",), errors=["Test error", "Other error"], warnings=[]
        )
    ]
    assert not Translation.objects.filter(string="new translation").exists()

    po_translation.refresh_from_db()

    assert po_translation.pretranslated
    assert po_translation.active
    assert not po_translation.rejected
    assert not ChangedEntityLocale.objects.filter(entity=po_translation.entity).exists()
    assert not ActionLog.objects.filter(
        action_type=ActionLog.ActionType.TRANSLATION_CREATED, performed_by=uploader
    ).exists()


@pytest.mark.django_db
def test_upload_pretranslations_keeps_matching_fuzzy_with_warnings(
    monkeypatch, project_locale_a, resource, po_translation, uploader
):
    """A matching fuzzy translation with warnings stays fuzzy and exported as it is."""
    monkeypatch.setattr(
        sync_upload, "run_checks", _failing_checks({"pndbWarnings": ["Test warning"]})
    )
    po_translation.fuzzy = True
    po_translation.active = True
    po_translation.string = "new translation"
    po_translation.value = ["new translation"]
    po_translation.save()
    ChangedEntityLocale.objects.all().delete()

    result = _import(
        import_uploaded_pretranslations, project_locale_a, resource, uploader
    )

    assert result.converted == 0
    assert len(result.failed_checks) == 1

    po_translation.refresh_from_db()

    assert po_translation.fuzzy
    assert not po_translation.pretranslated
    assert not ChangedEntityLocale.objects.filter(entity=po_translation.entity).exists()


@pytest.mark.django_db
def test_upload_pretranslations_reports_missing_placeholder(
    project_locale_a, android_entity, uploader
):
    """A dropped placeholder is caught, though it is not a check stored in the DB."""
    result = _import(
        import_uploaded_pretranslations,
        project_locale_a,
        android_entity.resource,
        uploader,
        upload=_android_upload_without_placeholder(),
    )

    assert result.created == 0
    assert result.failed_checks == [
        FailedCheck(
            key=("page_at",),
            errors=[],
            warnings=["Placeholder {$arg1} not found in translation"],
        )
    ]
    assert not Translation.objects.filter(entity=android_entity).exists()


@pytest.mark.django_db
def test_upload_pretranslations_skips_matching_translation_with_errors(
    monkeypatch, project_locale_a, resource, po_translation, uploader
):
    """A matching translation that fails checks is not converted, and is not deleted."""
    monkeypatch.setattr(
        sync_upload, "run_checks", _failing_checks({"pErrors": ["Test error"]})
    )
    po_translation.fuzzy = True
    po_translation.active = True
    po_translation.string = "new translation"
    po_translation.value = ["new translation"]
    po_translation.save()
    ChangedEntityLocale.objects.all().delete()

    result = _import(
        import_uploaded_pretranslations, project_locale_a, resource, uploader
    )

    assert result.converted == 0
    assert result.failed_checks == [
        FailedCheck(key=("test_key",), errors=["Test error"], warnings=[])
    ]

    po_translation.refresh_from_db()

    assert po_translation.fuzzy
    assert not po_translation.pretranslated
    assert not po_translation.rejected
    assert po_translation.active
    assert not ChangedEntityLocale.objects.filter(entity=po_translation.entity).exists()


@pytest.mark.django_db
def test_upload_pretranslations_updates_stats_and_marks_changed(
    project_locale_a, resource, untranslated_entity, uploader
):
    """Stored pretranslations are counted in stats, and synced by the next sync."""
    _import(
        import_uploaded_pretranslations,
        project_locale_a,
        resource,
        uploader,
        contents='msgid "other_key"\nmsgstr "pretranslation"',
    )

    assert (
        TranslatedResource.objects.get(
            resource=resource, locale=project_locale_a.locale
        ).pretranslated_strings
        == 1
    )
    assert ChangedEntityLocale.objects.filter(
        entity=untranslated_entity, locale=project_locale_a.locale
    ).exists()


@pytest.mark.django_db
def test_upload_pretranslations_drops_replacement_with_warnings(
    monkeypatch, project_locale_a, resource, po_translation, uploader
):
    """Warnings keep a pretranslation from being exported, so it is not stored either."""
    monkeypatch.setattr(
        sync_upload, "run_checks", _failing_checks({"pndbWarnings": ["Test warning"]})
    )
    po_translation.pretranslated = True
    po_translation.active = True
    po_translation.save()
    ChangedEntityLocale.objects.all().delete()

    result = _import(
        import_uploaded_pretranslations, project_locale_a, resource, uploader
    )

    assert result.replaced == 0
    assert result.failed_checks == [
        FailedCheck(key=("test_key",), errors=[], warnings=["Test warning"])
    ]
    assert not Translation.objects.filter(string="new translation").exists()

    po_translation.refresh_from_db()

    assert po_translation.pretranslated
    assert po_translation.active
    assert not po_translation.rejected
    assert not ChangedEntityLocale.objects.filter(entity=po_translation.entity).exists()


@pytest.mark.django_db
def test_upload_pretranslations_updates_latest_translation(
    project_locale_a, resource, untranslated_entity, uploader
):
    """Latest activity is updated, as it would be by Translation.save()."""
    _import(
        import_uploaded_pretranslations,
        project_locale_a,
        resource,
        uploader,
        contents='msgid "other_key"\nmsgstr "pretranslation"',
    )

    pretranslation = Translation.objects.get(entity=untranslated_entity)
    project_locale_a.refresh_from_db()

    assert (
        TranslatedResource.objects.get(
            resource=resource, locale=project_locale_a.locale
        ).latest_translation
        == pretranslation
    )
    assert project_locale_a.latest_translation == pretranslation


@pytest.mark.django_db
def test_upload_pretranslations_skips_approved(
    project_locale_a, resource, po_translation, uploader
):
    """A string with an approved translation is left untouched."""
    po_translation.approved = True
    po_translation.active = True
    po_translation.save()

    result = _import(
        import_uploaded_pretranslations, project_locale_a, resource, uploader
    )

    assert result.skipped == 1
    assert result.created == 0

    po_translation.refresh_from_db()

    assert po_translation.approved
    assert Translation.objects.filter(entity=po_translation.entity).count() == 1


@pytest.mark.django_db
def test_upload_pretranslations_replaces_fuzzy(
    project_locale_a, resource, po_translation, uploader
):
    """A different fuzzy translation is rejected and replaced."""
    po_translation.fuzzy = True
    po_translation.active = True
    po_translation.save()

    result = _import(
        import_uploaded_pretranslations, project_locale_a, resource, uploader
    )

    assert result.replaced == 1
    assert result.skipped == 0

    po_translation.refresh_from_db()

    assert po_translation.rejected
    assert not po_translation.fuzzy
    assert not po_translation.active

    new_translation = Translation.objects.get(string="new translation")

    assert new_translation.pretranslated
    assert new_translation.active
    assert not new_translation.fuzzy


@pytest.mark.django_db
def test_upload_pretranslations_converts_matching_fuzzy(
    project_locale_a, resource, po_translation, uploader
):
    """A fuzzy translation matching the upload becomes a pretranslation."""
    author = po_translation.user
    po_translation.fuzzy = True
    po_translation.active = True
    po_translation.string = "new translation"
    po_translation.value = ["new translation"]
    po_translation.save()

    result = _import(
        import_uploaded_pretranslations, project_locale_a, resource, uploader
    )

    assert result.converted == 1
    assert Translation.objects.filter(entity=po_translation.entity).count() == 1

    po_translation.refresh_from_db()

    assert po_translation.pretranslated
    assert po_translation.active
    assert not po_translation.fuzzy
    assert not po_translation.rejected
    assert po_translation.user == author


@pytest.mark.django_db
def test_upload_pretranslations_replaces_pretranslation(
    project_locale_a, resource, po_translation, uploader
):
    """A different pretranslation is rejected and replaced."""
    po_translation.pretranslated = True
    po_translation.active = True
    po_translation.save()

    result = _import(
        import_uploaded_pretranslations, project_locale_a, resource, uploader
    )

    assert result.replaced == 1
    assert result.created == 0

    po_translation.refresh_from_db()

    assert po_translation.rejected
    assert not po_translation.pretranslated
    assert not po_translation.active
    assert po_translation.rejected_user == uploader

    new_translation = Translation.objects.get(string="new translation")

    assert new_translation.pretranslated
    assert new_translation.active
    assert ActionLog.objects.filter(
        performed_by=uploader,
        action_type=ActionLog.ActionType.TRANSLATION_REJECTED,
        translation=po_translation,
    ).exists()


@pytest.mark.django_db
def test_upload_pretranslations_reactivates_matching_pretranslation(
    project_locale_a, resource, po_translation, uploader
):
    """A matching pretranslation left inactive by a later suggestion is activated."""
    po_translation.approved = False
    po_translation.pretranslated = True
    po_translation.active = False
    po_translation.string = "new translation"
    po_translation.value = ["new translation"]
    po_translation.save()
    suggestion = TranslationFactory.create(
        entity=po_translation.entity,
        locale=project_locale_a.locale,
        string="a suggestion",
        value=["a suggestion"],
        active=True,
    )

    result = _import(
        import_uploaded_pretranslations, project_locale_a, resource, uploader
    )

    assert result.unchanged == 0
    assert result.converted == 1

    po_translation.refresh_from_db()
    suggestion.refresh_from_db()

    assert po_translation.pretranslated
    assert po_translation.active
    assert not suggestion.active
    assert not suggestion.rejected


@pytest.mark.django_db
def test_upload_pretranslations_unchanged(
    project_locale_a, resource, po_translation, uploader
):
    """An identical pretranslation is reported as unchanged."""
    po_translation.pretranslated = True
    po_translation.active = True
    po_translation.string = "new translation"
    po_translation.value = ["new translation"]
    po_translation.save()

    result = _import(
        import_uploaded_pretranslations, project_locale_a, resource, uploader
    )

    assert result.unchanged == 1
    assert Translation.objects.filter(entity=po_translation.entity).count() == 1


@pytest.mark.django_db
def test_upload_pretranslations_flags_matching_suggestion(
    project_locale_a, resource, po_translation, uploader
):
    """A suggestion matching the upload becomes a pretranslation, keeping its author."""
    author = po_translation.user
    po_translation.string = "new translation"
    po_translation.value = ["new translation"]
    po_translation.save()

    result = _import(
        import_uploaded_pretranslations, project_locale_a, resource, uploader
    )

    assert result.converted == 1
    assert Translation.objects.filter(entity=po_translation.entity).count() == 1

    po_translation.refresh_from_db()

    assert po_translation.pretranslated
    assert po_translation.active
    assert not po_translation.approved
    assert po_translation.user == author


@pytest.mark.django_db
def test_upload_pretranslations_clears_stale_checks_of_matching_suggestion(
    project_locale_a, resource, po_translation, uploader
):
    """A converted suggestion loses the checks stored for it, as it passes them now."""
    po_translation.string = "new translation"
    po_translation.value = ["new translation"]
    po_translation.save()
    # Checks stored when the translation was written, before they changed.
    Warning.objects.create(
        library="p", message="Stale warning", translation=po_translation
    )
    Error.objects.create(library="p", message="Stale error", translation=po_translation)

    result = _import(
        import_uploaded_pretranslations, project_locale_a, resource, uploader
    )

    assert result.converted == 1
    assert not po_translation.warnings.exists()
    assert not po_translation.errors.exists()

    # Stale checks would have kept the pretranslation out of the stats and the export.
    translated_resource = TranslatedResource.objects.get(
        resource=resource, locale=project_locale_a.locale
    )

    assert translated_resource.pretranslated_strings == 1
    assert translated_resource.strings_with_warnings == 0
    assert translated_resource.strings_with_errors == 0


@pytest.mark.django_db
def test_upload_pretranslations_keeps_other_suggestions(
    project_locale_a, resource, po_translation, uploader
):
    """Suggestions that do not match the upload are kept as unreviewed suggestions."""
    po_translation.active = True
    po_translation.save()

    result = _import(
        import_uploaded_pretranslations, project_locale_a, resource, uploader
    )

    assert result.created == 1

    po_translation.refresh_from_db()

    assert not po_translation.rejected
    assert not po_translation.pretranslated
    assert not po_translation.active

    new_translation = Translation.objects.get(string="new translation")

    assert new_translation.pretranslated
    assert new_translation.active


@pytest.mark.django_db
def test_upload_pretranslations_unknown_keys_ignored(
    project_locale_a, resource, po_translation, uploader
):
    result = _import(
        import_uploaded_pretranslations,
        project_locale_a,
        resource,
        uploader,
        contents='msgid "test_key"\nmsgstr "new translation"\n\n'
        'msgid "no_such_key"\nmsgstr "x"\n',
    )

    assert result.created == 1
    assert result.undefined_keys == [("no_such_key",)]


@pytest.mark.django_db
def test_upload_pretranslations_conflicts_with_concurrent_approval_of_pretranslation(
    monkeypatch, project_locale_a, resource, po_translation, uploader, admin
):
    """A pretranslation approved mid-import is not rejected and replaced."""
    po_translation.pretranslated = True
    po_translation.active = True
    po_translation.save()

    _approve_during_import(monkeypatch, po_translation, admin)
    _import_conflicts(
        import_uploaded_pretranslations, project_locale_a, resource, uploader
    )

    # The import is rolled back, which also undoes the approval made inside it.
    po_translation.refresh_from_db()

    assert not po_translation.rejected
    assert po_translation.pretranslated
    assert po_translation.active
    assert Translation.objects.filter(entity=po_translation.entity).count() == 1


@pytest.mark.django_db
def test_upload_pretranslations_conflicts_with_concurrent_approval_of_suggestion(
    monkeypatch, project_locale_a, resource, po_translation, uploader, admin
):
    """A matching suggestion approved mid-import is not converted to a pretranslation."""
    po_translation.active = True
    po_translation.string = "new translation"
    po_translation.value = ["new translation"]
    po_translation.save()

    _approve_during_import(monkeypatch, po_translation, admin)
    _import_conflicts(
        import_uploaded_pretranslations, project_locale_a, resource, uploader
    )

    po_translation.refresh_from_db()

    assert not po_translation.pretranslated
    assert not po_translation.approved
    assert Translation.objects.filter(entity=po_translation.entity).count() == 1


@pytest.mark.django_db
def test_upload_pretranslations_conflicts_with_concurrent_rejection_of_suggestion(
    monkeypatch, project_locale_a, resource, po_translation, uploader, admin
):
    """A matching suggestion rejected mid-import is not converted to a pretranslation."""
    po_translation.active = True
    po_translation.string = "new translation"
    po_translation.value = ["new translation"]
    po_translation.save()

    _review_during_import(monkeypatch, lambda: po_translation.reject(admin))
    _import_conflicts(
        import_uploaded_pretranslations, project_locale_a, resource, uploader
    )

    po_translation.refresh_from_db()

    assert not po_translation.rejected
    assert not po_translation.pretranslated
    assert Translation.objects.filter(entity=po_translation.entity).count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("field", ["pretranslated", "fuzzy"])
def test_upload_pretranslations_conflicts_with_concurrent_precedence_change(
    monkeypatch, project_locale_a, resource, po_translation, uploader, field
):
    """A suggestion that gains precedence mid-import is not just deactivated."""
    po_translation.active = True
    po_translation.save()

    _review_during_import(
        monkeypatch,
        lambda: Translation.objects.filter(pk=po_translation.pk).update(
            **{field: True}
        ),
    )
    _import_conflicts(
        import_uploaded_pretranslations, project_locale_a, resource, uploader
    )

    # The import is rolled back, which also undoes the change made inside it.
    po_translation.refresh_from_db()

    assert po_translation.active
    assert not getattr(po_translation, field)
    assert Translation.objects.filter(entity=po_translation.entity).count() == 1


# Suggestions


@pytest.mark.django_db
def test_upload_suggestions_creates_suggestion(
    project_locale_a, resource, untranslated_entity, uploader
):
    """An untranslated string gets a new suggestion, authored by the uploader."""
    result = _import(
        import_uploaded_suggestions,
        project_locale_a,
        resource,
        uploader,
        contents='msgid "other_key"\nmsgstr "a suggestion"',
    )

    assert result.created == 1
    assert result.restored == 0
    assert result.unchanged == 0
    assert result.failed_checks == []
    assert result.undefined_keys == []

    translation = Translation.objects.get(entity=untranslated_entity)

    assert translation.string == "a suggestion"
    assert translation.active
    assert not translation.approved
    assert not translation.pretranslated
    assert not translation.fuzzy
    assert not translation.rejected
    assert translation.user == uploader
    assert ActionLog.objects.filter(
        performed_by=uploader,
        action_type=ActionLog.ActionType.TRANSLATION_CREATED,
        translation=translation,
    ).exists()


@pytest.mark.django_db
def test_upload_suggestions_ignores_fuzzy_flag(
    project_locale_a, resource, untranslated_entity, uploader
):
    """A translation marked as fuzzy in the file is stored as a plain suggestion."""
    result = _import(
        import_uploaded_suggestions,
        project_locale_a,
        resource,
        uploader,
        contents='#, fuzzy\nmsgid "other_key"\nmsgstr "a suggestion"',
    )

    assert result.created == 1

    translation = Translation.objects.get(entity=untranslated_entity)

    assert not translation.fuzzy
    assert translation.active


@pytest.mark.django_db
@pytest.mark.parametrize(
    "state",
    [
        {},
        {"approved": True},
        {"pretranslated": True},
        {"fuzzy": True},
    ],
)
def test_upload_suggestions_skips_matching_translation(
    project_locale_a, resource, po_translation, uploader, state
):
    """An unrejected translation Pontoon has is not suggested again, in any state."""
    po_translation.string = "new translation"
    po_translation.value = ["new translation"]
    po_translation.active = True
    for name, value in state.items():
        setattr(po_translation, name, value)
    po_translation.save()

    result = _import(import_uploaded_suggestions, project_locale_a, resource, uploader)

    assert result.unchanged == 1
    assert result.created == 0
    assert result.restored == 0
    assert Translation.objects.filter(entity=po_translation.entity).count() == 1

    po_translation.refresh_from_db()

    # The matched translation keeps the review state it had, fuzzy included.
    for name, value in state.items():
        assert getattr(po_translation, name) == value
    assert not po_translation.rejected
    assert po_translation.active


@pytest.mark.django_db
def test_upload_suggestions_keeps_approved_translation_active(
    project_locale_a, resource, po_translation, uploader
):
    """A suggestion for an approved string is stored, without becoming active."""
    po_translation.approved = True
    po_translation.active = True
    po_translation.save()

    result = _import(import_uploaded_suggestions, project_locale_a, resource, uploader)

    assert result.created == 1

    po_translation.refresh_from_db()
    suggestion = Translation.objects.get(string="new translation")

    assert po_translation.approved
    assert po_translation.active
    assert not po_translation.rejected
    assert not suggestion.active


@pytest.mark.django_db
def test_upload_suggestions_deactivates_previous_suggestion(
    project_locale_a, resource, po_translation, uploader
):
    """As the newest suggestion, the uploaded one is shown instead of the previous."""
    po_translation.active = True
    po_translation.save()

    result = _import(import_uploaded_suggestions, project_locale_a, resource, uploader)

    assert result.created == 1

    po_translation.refresh_from_db()
    suggestion = Translation.objects.get(string="new translation")

    assert suggestion.active
    assert not po_translation.active
    assert not po_translation.rejected


@pytest.mark.django_db
def test_upload_suggestions_drops_errors(
    monkeypatch, project_locale_a, resource, po_translation, uploader
):
    """A suggestion with errors is not stored, as the editor rejects it too."""
    monkeypatch.setattr(
        sync_upload, "run_checks", _failing_checks({"pErrors": ["Test error"]})
    )

    result = _import(import_uploaded_suggestions, project_locale_a, resource, uploader)

    assert result.created == 0
    assert result.failed_checks == [
        FailedCheck(key=("test_key",), errors=["Test error"], warnings=[])
    ]
    assert not Translation.objects.filter(string="new translation").exists()


@pytest.mark.django_db
def test_upload_suggestions_stores_warnings(
    monkeypatch, project_locale_a, resource, po_translation, uploader
):
    """A suggestion with warnings is stored, with its warnings, for a reviewer to see."""
    monkeypatch.setattr(
        sync_upload, "run_checks", _failing_checks({"pWarnings": ["Test warning"]})
    )

    result = _import(import_uploaded_suggestions, project_locale_a, resource, uploader)

    assert result.created == 1
    assert result.failed_checks == []

    suggestion = Translation.objects.get(string="new translation")

    assert [w.message for w in suggestion.warnings.all()] == ["Test warning"]
    assert not suggestion.errors.exists()


@pytest.mark.django_db
def test_upload_suggestions_stores_missing_placeholder_warning(
    project_locale_a, android_entity, uploader
):
    """A dropped placeholder is only a warning, so the suggestion is still stored."""
    result = _import(
        import_uploaded_suggestions,
        project_locale_a,
        android_entity.resource,
        uploader,
        upload=_android_upload_without_placeholder(),
    )

    assert result.created == 1
    assert result.failed_checks == []

    suggestion = Translation.objects.get(entity=android_entity)

    assert [w.message for w in suggestion.warnings.all()] == [
        "Placeholder {$arg1} not found in translation"
    ]


@pytest.mark.django_db
def test_upload_suggestions_unknown_keys_ignored(
    project_locale_a, resource, po_translation, uploader
):
    result = _import(
        import_uploaded_suggestions,
        project_locale_a,
        resource,
        uploader,
        contents='msgid "test_key"\nmsgstr "new translation"\n\n'
        'msgid "no_such_key"\nmsgstr "x"\n',
    )

    assert result.created == 1
    assert result.undefined_keys == [("no_such_key",)]


@pytest.mark.django_db
def test_upload_suggestions_updates_stats_without_marking_changed(
    project_locale_a, resource, untranslated_entity, uploader
):
    """Suggestions are counted in stats, but never exported, so nothing is changed."""
    ChangedEntityLocale.objects.all().delete()

    _import(
        import_uploaded_suggestions,
        project_locale_a,
        resource,
        uploader,
        contents='msgid "other_key"\nmsgstr "a suggestion"',
    )

    translated_resource = TranslatedResource.objects.get(
        resource=resource, locale=project_locale_a.locale
    )

    # `po_translation` is an unreviewed suggestion of the other entity.
    assert translated_resource.unreviewed_strings == 2
    assert translated_resource.approved_strings == 0
    assert not ChangedEntityLocale.objects.exists()


@pytest.mark.django_db
def test_upload_suggestions_updates_latest_translation(
    project_locale_a, resource, untranslated_entity, uploader
):
    """Latest activity is updated, as it would be by Translation.save()."""
    _import(
        import_uploaded_suggestions,
        project_locale_a,
        resource,
        uploader,
        contents='msgid "other_key"\nmsgstr "a suggestion"',
    )

    suggestion = Translation.objects.get(entity=untranslated_entity)
    project_locale_a.refresh_from_db()

    assert (
        TranslatedResource.objects.get(
            resource=resource, locale=project_locale_a.locale
        ).latest_translation
        == suggestion
    )
    assert project_locale_a.latest_translation == suggestion


@pytest.mark.django_db
def test_upload_suggestions_restores_rejected_translation(
    project_locale_a, resource, po_translation, uploader, admin
):
    """A rejected translation matching the upload is un-rejected, not duplicated."""
    author = po_translation.user
    date = po_translation.date
    po_translation.string = "new translation"
    po_translation.value = ["new translation"]
    po_translation.save()
    po_translation.reject(admin)

    result = _import(import_uploaded_suggestions, project_locale_a, resource, uploader)

    assert result.restored == 1
    assert result.created == 0
    assert result.unchanged == 0
    assert Translation.objects.filter(entity=po_translation.entity).count() == 1

    po_translation.refresh_from_db()

    assert not po_translation.rejected
    assert not po_translation.approved
    assert not po_translation.pretranslated
    assert not po_translation.fuzzy
    assert po_translation.active
    # The restored suggestion keeps its own author and date.
    assert po_translation.user == author
    assert po_translation.date == date
    assert po_translation.unrejected_user == uploader
    assert ActionLog.objects.filter(
        performed_by=uploader,
        action_type=ActionLog.ActionType.TRANSLATION_UNREJECTED,
        translation=po_translation,
    ).exists()


@pytest.mark.django_db
def test_upload_suggestions_restored_stays_behind_approved(
    project_locale_a, resource, po_translation, uploader, admin
):
    """Restoring a suggestion does not take the active slot from an approved one."""
    po_translation.string = "new translation"
    po_translation.value = ["new translation"]
    po_translation.save()
    po_translation.reject(admin)
    approved = TranslationFactory.create(
        entity=po_translation.entity,
        locale=project_locale_a.locale,
        string="the approved one",
        value=["the approved one"],
        approved=True,
        active=True,
    )

    result = _import(import_uploaded_suggestions, project_locale_a, resource, uploader)

    assert result.restored == 1

    po_translation.refresh_from_db()
    approved.refresh_from_db()

    assert not po_translation.rejected
    assert not po_translation.active
    assert approved.active
    assert approved.approved


@pytest.mark.django_db
def test_upload_suggestions_restored_stays_behind_newer_suggestion(
    project_locale_a, resource, po_translation, uploader, admin
):
    """A restored suggestion older than the active one does not become active."""
    po_translation.string = "new translation"
    po_translation.value = ["new translation"]
    po_translation.save()
    po_translation.reject(admin)
    newer = TranslationFactory.create(
        entity=po_translation.entity,
        locale=project_locale_a.locale,
        string="a newer suggestion",
        value=["a newer suggestion"],
        active=True,
        date=po_translation.date + timedelta(days=1),
    )

    result = _import(import_uploaded_suggestions, project_locale_a, resource, uploader)

    assert result.restored == 1

    po_translation.refresh_from_db()
    newer.refresh_from_db()

    assert not po_translation.rejected
    assert not po_translation.active
    assert newer.active


@pytest.mark.django_db
def test_upload_suggestions_restore_counted_in_stats(
    project_locale_a, resource, po_translation, uploader, admin
):
    """A restored suggestion is unreviewed again, so it is counted in stats."""
    po_translation.string = "new translation"
    po_translation.value = ["new translation"]
    po_translation.save()
    po_translation.reject(admin)

    translated_resource = TranslatedResource.objects.get(
        resource=resource, locale=project_locale_a.locale
    )

    assert translated_resource.unreviewed_strings == 0

    _import(import_uploaded_suggestions, project_locale_a, resource, uploader)

    translated_resource.refresh_from_db()

    assert translated_resource.unreviewed_strings == 1


@pytest.mark.django_db
def test_upload_suggestions_does_not_restore_translation_with_errors(
    monkeypatch, project_locale_a, resource, po_translation, uploader, admin
):
    """A rejected translation that no longer passes checks stays rejected."""
    monkeypatch.setattr(
        sync_upload, "run_checks", _failing_checks({"pErrors": ["Test error"]})
    )
    po_translation.string = "new translation"
    po_translation.value = ["new translation"]
    po_translation.save()
    po_translation.reject(admin)

    result = _import(import_uploaded_suggestions, project_locale_a, resource, uploader)

    assert result.restored == 0
    assert result.failed_checks == [
        FailedCheck(key=("test_key",), errors=["Test error"], warnings=[])
    ]

    po_translation.refresh_from_db()

    assert po_translation.rejected
    assert po_translation.unrejected_user is None


@pytest.mark.django_db
def test_upload_suggestions_refreshes_checks_of_restored_translation(
    monkeypatch, project_locale_a, resource, po_translation, uploader, admin
):
    """The checks stored for a restored translation are the ones just run for it."""
    monkeypatch.setattr(
        sync_upload, "run_checks", _failing_checks({"pWarnings": ["Fresh warning"]})
    )
    po_translation.string = "new translation"
    po_translation.value = ["new translation"]
    po_translation.save()
    po_translation.reject(admin)
    # Checks stored when the translation was written, before they changed.
    Warning.objects.create(
        library="p", message="Stale warning", translation=po_translation
    )
    Error.objects.create(library="p", message="Stale error", translation=po_translation)

    result = _import(import_uploaded_suggestions, project_locale_a, resource, uploader)

    assert result.restored == 1
    assert [w.message for w in po_translation.warnings.all()] == ["Fresh warning"]
    assert not po_translation.errors.exists()


@pytest.mark.django_db
def test_upload_suggestions_conflicts_with_concurrent_approval(
    monkeypatch, project_locale_a, resource, po_translation, uploader, admin
):
    """A suggestion approved mid-import is not deactivated by the uploaded one."""
    po_translation.active = True
    po_translation.save()

    _approve_during_import(monkeypatch, po_translation, admin)
    _import_conflicts(import_uploaded_suggestions, project_locale_a, resource, uploader)

    # The import is rolled back, which also undoes the approval made inside it.
    po_translation.refresh_from_db()

    assert po_translation.active
    assert not po_translation.approved
    assert Translation.objects.filter(entity=po_translation.entity).count() == 1


@pytest.mark.django_db
@pytest.mark.parametrize("field", ["pretranslated", "fuzzy"])
def test_upload_suggestions_conflicts_with_concurrent_precedence_change(
    monkeypatch, project_locale_a, resource, po_translation, uploader, field
):
    """A suggestion that gains precedence mid-import is not deactivated."""
    po_translation.active = True
    po_translation.save()

    _review_during_import(
        monkeypatch,
        lambda: Translation.objects.filter(pk=po_translation.pk).update(
            **{field: True}
        ),
    )
    _import_conflicts(import_uploaded_suggestions, project_locale_a, resource, uploader)

    # The import is rolled back, which also undoes the change made inside it.
    po_translation.refresh_from_db()

    assert po_translation.active
    assert not getattr(po_translation, field)
    assert Translation.objects.filter(entity=po_translation.entity).count() == 1


@pytest.mark.django_db
def test_upload_suggestions_conflicts_with_concurrent_rejection_of_approved(
    monkeypatch, project_locale_a, resource, po_translation, uploader, admin
):
    """The approved translation an inactive suggestion defers to is rejected mid-import."""
    po_translation.approved = True
    po_translation.active = True
    po_translation.save()

    _review_during_import(monkeypatch, lambda: po_translation.reject(admin))
    _import_conflicts(import_uploaded_suggestions, project_locale_a, resource, uploader)

    # The import is rolled back, which also undoes the rejection made inside it.
    po_translation.refresh_from_db()

    assert po_translation.approved
    assert po_translation.active
    assert Translation.objects.filter(entity=po_translation.entity).count() == 1


@pytest.mark.django_db
def test_upload_suggestions_conflicts_with_concurrent_unrejection(
    monkeypatch, project_locale_a, resource, po_translation, uploader, admin
):
    """A rejected translation un-rejected mid-import is not restored a second time."""
    po_translation.string = "new translation"
    po_translation.value = ["new translation"]
    po_translation.save()
    po_translation.reject(admin)

    _review_during_import(monkeypatch, lambda: po_translation.unreject(admin))
    _import_conflicts(import_uploaded_suggestions, project_locale_a, resource, uploader)

    # The import is rolled back, which also undoes the un-rejection made inside it.
    po_translation.refresh_from_db()

    assert po_translation.rejected
    assert po_translation.unrejected_user is None
    assert not ActionLog.objects.filter(
        action_type=ActionLog.ActionType.TRANSLATION_UNREJECTED,
        translation=po_translation,
    ).exists()


@pytest.mark.django_db
def test_upload_suggestions_conflicts_with_concurrent_deletion(
    monkeypatch, project_locale_a, resource, po_translation, uploader
):
    """A suggestion deleted mid-import, which the upload would deactivate, is a conflict."""
    po_translation.active = True
    po_translation.save()

    _review_during_import(monkeypatch, lambda: po_translation.delete())
    _import_conflicts(import_uploaded_suggestions, project_locale_a, resource, uploader)

    assert not Translation.objects.filter(string="new translation").exists()


@pytest.mark.django_db
@pytest.mark.parametrize(
    "importer", [import_uploaded_pretranslations, import_uploaded_suggestions]
)
def test_upload_locks_target_before_reading_translations(
    importer, project_locale_a, resource, po_translation, uploader
):
    """The lock that serializes concurrent imports is taken before the read it guards."""
    with CaptureQueriesContext(connection) as queries:
        _import(importer, project_locale_a, resource, uploader)

    statements = [query["sql"] for query in queries.captured_queries]
    lock = next(
        i
        for i, sql in enumerate(statements)
        if "base_translatedresource" in sql and "FOR UPDATE" in sql
    )
    read = next(
        i for i, sql in enumerate(statements) if 'FROM "base_translation"' in sql
    )

    assert lock < read
