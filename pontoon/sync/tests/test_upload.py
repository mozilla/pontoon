from types import SimpleNamespace

import pytest

from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import transaction

from pontoon.actionlog.models import ActionLog
from pontoon.base.models import (
    ChangedEntityLocale,
    Resource,
    TranslatedResource,
    Translation,
)
from pontoon.sync import upload as sync_upload
from pontoon.sync.upload import (
    FailedCheck,
    UploadConflictError,
    UploadError,
    import_uploaded_file,
    import_uploaded_pretranslations,
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
    conflict check guards.
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
