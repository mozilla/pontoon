import pytest

from pontoon.base.models import Translation
from pontoon.base.tests import po_file


@pytest.yield_fixture
def translator_a(
    member, project_locale_a,
):
    """
    A translator is required to test upload of the new strings.
    """
    project_locale_a.locale.translators_group.user_set.add(member.user)

    yield member


@pytest.yield_fixture
def readonly_project_locale(project_locale_a):
    project_locale_a.readonly = True
    project_locale_a.save()

    yield project_locale_a


@pytest.yield_fixture
def po_translation(translation_a):
    """
    Some tests require entity with non-empty key.
    """
    translation_a.entity.key = "test_key"
    translation_a.entity.save()

    yield translation_a


def upload(client, **args):
    """
    Shortcut function to call /upload/ view.
    """
    response = client.post("/upload/", args,)

    return response


@pytest.mark.django_db
def test_upload_login_required(
    client, project_a, locale_a,
):
    """
    Return HTTP 403 if user is anonymous
    """
    response = upload(
        client, slug=project_a.slug, code=locale_a.code, part="resource_a.po",
    )

    assert response.status_code == 302
    assert response.url == "/403"


@pytest.mark.django_db
@pytest.mark.parametrize(
    "missing_parameter", ("slug", "code", "resource_a.po",),
)
def test_upload_invalid_parameters(
    member, missing_parameter, project_a, locale_a,
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
    client, translator_a, project_locale_a,
):
    response = upload(
        translator_a.client,
        slug=project_locale_a.project.slug,
        code=project_locale_a.locale.code,
        part="resource_a.po",
    )
    assert response.status_code == 303

    redir = client.get(response["Location"])
    assert redir.status_code == 404


@pytest.mark.django_db
def test_upload_cannot_translate(
    member, project_locale_a,
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
    translator_a, readonly_project_locale,
):
    response = upload(
        translator_a.client,
        slug=readonly_project_locale.project.slug,
        code=readonly_project_locale.locale.code,
        part="resource_a.po",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_upload_file(
    translator_a, project_locale_a, po_translation,
):
    """
    Test a positive upload which changes the translation.
    """
    with po_file(test_key="new translation") as fp:
        response = upload(
            translator_a.client,
            slug=project_locale_a.project.slug,
            code=project_locale_a.locale.code,
            part=po_translation.entity.resource.path,
            uploadfile=fp,
        )
        assert response.status_code == 303

        translation = Translation.objects.get(string="new translation")

        assert translation.entity.key == "test_key"
        assert translation.entity.resource.path == "resource_a.po"
        assert translation.approved
        assert not translation.warnings.exists()
        assert not translation.errors.exists()
