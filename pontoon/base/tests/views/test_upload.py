from tempfile import NamedTemporaryFile

import pytest

from django.contrib.messages import get_messages

from pontoon.base.models import ChangedEntityLocale, Translation
from pontoon.test.factories import EntityFactory, TranslationFactory


@pytest.fixture
def translator_a(
    member,
    project_locale_a,
):
    """
    A translator is required to test upload of the new strings.
    """
    project_locale_a.locale.translators_group.user_set.add(member.user)

    yield member


@pytest.fixture
def readonly_project_locale(project_locale_a):
    project_locale_a.readonly = True
    project_locale_a.save()

    yield project_locale_a


@pytest.fixture
def po_translation(translation_a):
    """
    Some tests require entity with non-empty key.
    """
    translation_a.entity.key = ["test_key"]
    translation_a.entity.save()

    yield translation_a


def upload(client, **args):
    """
    Shortcut function to call /upload/ view.
    """
    response = client.post(
        "/upload/",
        args,
    )

    return response


@pytest.fixture
def approved_po_translation(po_translation):
    po_translation.approved = True
    po_translation.active = True
    po_translation.save()

    yield po_translation


@pytest.fixture
def upload_po(translator_a, project_locale_a, po_translation):
    """
    Upload the given contents as a .po file for the `po_translation` resource,
    returning the list of (tags, message) pairs.
    """

    def _upload_po(po_contents):
        with NamedTemporaryFile("w+", suffix=".po") as fp:
            fp.write(po_contents)
            fp.flush()
            response = upload(
                translator_a.client,
                slug=project_locale_a.project.slug,
                code=project_locale_a.locale.code,
                part=po_translation.entity.resource.path,
                uploadfile=open(fp.name),
            )
        assert response.status_code == 303
        return [(m.tags, m.message) for m in get_messages(response.wsgi_request)]

    return _upload_po


@pytest.mark.django_db
def test_upload_login_required(
    client,
    project_a,
    locale_a,
):
    """
    Return HTTP 403 if user is anonymous
    """
    response = upload(
        client,
        slug=project_a.slug,
        code=locale_a.code,
        part="resource_a.po",
    )

    assert response.status_code == 302
    assert response.url == "/403"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "missing_parameter",
    (
        "slug",
        "code",
        "resource_a.po",
    ),
)
def test_upload_invalid_parameters(
    member,
    missing_parameter,
    project_a,
    locale_a,
):
    """
    Check validation of parameters
    """
    params = {
        "slug": project_a.slug,
        "code": locale_a.code,
        "resource_a.po": "resource_a.po",
    }
    params.pop(missing_parameter, None)

    response = upload(member.client, **params)
    assert response.status_code == 404


@pytest.mark.django_db
def test_upload_missing_file(
    translator_a,
    project_locale_a,
):
    response = upload(
        translator_a.client,
        slug=project_locale_a.project.slug,
        code=project_locale_a.locale.code,
        part="resource_a.po",
    )
    assert response.status_code == 404


@pytest.mark.django_db
def test_upload_cannot_translate(
    member,
    project_locale_a,
):
    """
    Check if a member without permission gets HTTP 403
    """
    response = upload(
        member.client,
        slug=project_locale_a.project.slug,
        code=project_locale_a.locale.code,
        part="resource_a.po",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_upload_project_locale_is_readonly(
    translator_a,
    readonly_project_locale,
):
    response = upload(
        translator_a.client,
        slug=readonly_project_locale.project.slug,
        code=readonly_project_locale.locale.code,
        part="resource_a.po",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_upload_file(upload_po, po_translation):
    """
    Test a positive upload which changes the translation.
    """
    messages = upload_po('msgid "test_key"\nmsgstr "new translation"')
    assert messages == [
        ("upload success", "Translations from uploaded file: 1 updated, 0 unchanged.")
    ]

    translation = Translation.objects.get(string="new translation")
    assert translation.entity == po_translation.entity
    assert translation.approved
    assert translation.user
    assert not translation.warnings.exists()
    assert not translation.errors.exists()


@pytest.mark.django_db
def test_upload_is_additive(upload_po, approved_po_translation, locale_a):
    """
    Approved translations missing from the uploaded file are left untouched.
    """
    resource = approved_po_translation.entity.resource
    other_translation = TranslationFactory(
        entity=EntityFactory(resource=resource, string="other", key=["other_key"]),
        locale=locale_a,
        string="other translation",
        value=["other translation"],
        approved=True,
        active=True,
    )

    messages = upload_po('msgid "test_key"\nmsgstr "new translation"')
    assert messages == [
        ("upload success", "Translations from uploaded file: 1 updated, 0 unchanged.")
    ]

    approved_po_translation.refresh_from_db()
    assert not approved_po_translation.approved
    assert approved_po_translation.rejected
    assert (
        Translation.objects.get(
            entity=approved_po_translation.entity, approved=True
        ).string
        == "new translation"
    )

    other_translation.refresh_from_db()
    assert other_translation.approved
    assert other_translation.active
    assert not other_translation.rejected


@pytest.mark.django_db
def test_upload_approves_matching_suggestion(upload_po, po_translation, locale_a):
    """
    An uploaded translation matching an existing suggestion approves it,
    and the entity is still marked as changed for the next sync.
    """
    assert not po_translation.approved

    messages = upload_po(f'msgid "test_key"\nmsgstr "{po_translation.string}"')
    assert messages == [
        ("upload success", "Translations from uploaded file: 1 updated, 0 unchanged.")
    ]

    assert Translation.objects.filter(entity=po_translation.entity).count() == 1
    po_translation.refresh_from_db()
    assert po_translation.approved
    assert ChangedEntityLocale.objects.filter(
        entity=po_translation.entity, locale=locale_a
    ).exists()


@pytest.mark.django_db
def test_upload_identical_translation_is_ignored(upload_po, approved_po_translation):
    messages = upload_po(f'msgid "test_key"\nmsgstr "{approved_po_translation.string}"')
    assert messages == [
        ("upload info", "Translations from uploaded file: 0 updated, 1 unchanged.")
    ]

    assert (
        Translation.objects.filter(entity=approved_po_translation.entity).count() == 1
    )
    approved_po_translation.refresh_from_db()
    assert approved_po_translation.approved


@pytest.mark.django_db
def test_upload_undefined_keys_are_reported(upload_po, po_translation):
    """
    Translations for keys that are missing or obsolete in Pontoon are ignored.
    """
    resource = po_translation.entity.resource
    EntityFactory(resource=resource, string="old", key=["obsolete_key"], obsolete=True)

    messages = upload_po(
        'msgid "test_key"\nmsgstr "new translation"\n\n'
        'msgid "obsolete_key"\nmsgstr "obsolete translation"\n\n'
        'msgid "missing_key"\nmsgstr "missing translation"\n'
    )
    assert messages == [
        (
            "upload success",
            "Translations from uploaded file: 1 updated, 0 unchanged, "
            "2 not found in Pontoon.",
        )
    ]
    assert set(
        Translation.objects.filter(entity__resource=resource).values_list(
            "string", flat=True
        )
    ) == {po_translation.string, "new translation"}


@pytest.mark.django_db
def test_upload_ignores_translations_of_obsolete_entities(
    upload_po, po_translation, locale_a
):
    """
    A key removed and later re-added leaves an obsolete entity with the same key.
    If the new key is untranslated, the upload should fill it and be counted as
    translated, even if that matches the original translation in the obsolete key.
    """
    TranslationFactory(
        entity=EntityFactory(
            resource=po_translation.entity.resource,
            string="entity a",
            key=["test_key"],
            obsolete=True,
        ),
        locale=locale_a,
        string="new translation",
        value=["new translation"],
        approved=True,
        active=True,
    )

    messages = upload_po('msgid "test_key"\nmsgstr "new translation"')
    assert messages == [
        ("upload success", "Translations from uploaded file: 1 updated, 0 unchanged.")
    ]
    assert (
        Translation.objects.get(entity=po_translation.entity, approved=True).string
        == "new translation"
    )


@pytest.mark.django_db
def test_upload_file_without_translations(upload_po):
    messages = upload_po("# Just a comment\n")
    assert messages == [("error", "No translations found in uploaded file.")]
