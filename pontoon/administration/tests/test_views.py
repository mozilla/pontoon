import pytest

from django.urls import reverse

from pontoon.administration.forms import ProjectForm
from pontoon.base.models import ProjectLocale
from pontoon.test.factories import (
    LocaleFactory,
    ProjectFactory,
    ResourceFactory,
)


def _repository_form_data(project):
    data = {
        "repositories-TOTAL_FORMS": str(project.repositories.count()),
        "repositories-INITIAL_FORMS": str(project.repositories.count()),
    }
    for i, repo in enumerate(project.repositories.all()):
        data.update(
            {
                f"repositories-{i}-id": repo.pk,
                f"repositories-{i}-type": repo.type,
                f"repositories-{i}-url": repo.url,
                f"repositories-{i}-branch": repo.branch,
            }
        )
    return data


@pytest.mark.django_db
def test_manage_project(client_superuser):
    url = reverse("pontoon.admin.project.new")
    response = client_superuser.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_admin_hides_projects_without_repositories(client_superuser):
    repo_project = ProjectFactory.create()
    db_project = ProjectFactory.create(repositories=[])

    response = client_superuser.get(reverse("pontoon.admin"))
    assert response.status_code == 200
    assert repo_project.name.encode() in response.content
    assert db_project.name.encode() not in response.content


@pytest.mark.django_db
def test_manage_project_without_repositories(client_superuser, locale_a):
    project = ProjectFactory.create(locales=[locale_a], repositories=[])
    url = reverse("pontoon.admin.project", args=(project.slug,))

    response = client_superuser.get(url)
    assert response.status_code == 404

    response = client_superuser.post(url, {"pk": project.pk})
    assert response.status_code == 404


@pytest.mark.django_db
def test_manage_project_requires_repository(client_superuser, locale_a):
    project = ProjectFactory.create(locales=[locale_a])
    repository = project.repositories.get()
    url = reverse("pontoon.admin.project", args=(project.slug,))

    form_data = dict(ProjectForm(instance=project).initial)
    del form_data["deadline"]
    del form_data["contact"]
    form_data.update(
        {
            "pk": project.pk,
            "locales": [locale_a.id],
            "configuration_file": "",
            "externalresource_set-TOTAL_FORMS": "0",
            "externalresource_set-INITIAL_FORMS": "0",
            "tags-TOTAL_FORMS": "0",
            "tags-INITIAL_FORMS": "0",
            **_repository_form_data(project),
            "repositories-0-DELETE": "on",
        }
    )

    response = client_superuser.post(url, form_data)
    assert response.status_code == 200
    assert b"At least one repository is required." in response.content
    assert project.repositories.filter(pk=repository.pk).exists()


@pytest.mark.django_db
def test_manage_project_new_with_invalid_repository(client_superuser, locale_a):
    url = reverse("pontoon.admin.project.new")
    form_data = dict(ProjectForm().initial)
    form_data.update(
        {
            "name": "New Project",
            "slug": "new-project",
            "locales": [locale_a.id],
            "visibility": "public",
            "priority": 1,
            "set_translated_resources_from_repo": False,
            "externalresource_set-TOTAL_FORMS": "0",
            "externalresource_set-INITIAL_FORMS": "0",
            "repositories-TOTAL_FORMS": "1",
            "repositories-INITIAL_FORMS": "0",
            "repositories-0-type": "git",
            "repositories-0-url": "not a url",
        }
    )

    response = client_superuser.post(url, form_data)
    assert response.status_code == 200
    assert b". Error." in response.content

    form_data["repositories-0-url"] = ""
    response = client_superuser.post(url, form_data)
    assert response.status_code == 200
    assert b"This field is required." in response.content


@pytest.mark.django_db
def test_manage_project_translate_link_excludes_obsolete_resources(client_superuser):
    """Test that Translate link is only shown when non-obsolete resources exist."""
    locale_kl = LocaleFactory.create(code="tlh", name="Klingon")
    project = ProjectFactory.create(locales=[locale_kl])

    url = reverse("pontoon.admin.project", args=(project.slug,))
    translate_url = reverse(
        "pontoon.localizations.localization", args=(locale_kl.code, project.slug)
    )

    # add obsolete resource
    ResourceFactory.create(project=project, obsolete=True)

    response = client_superuser.get(url)
    assert response.status_code == 200
    assert translate_url.encode() not in response.content

    # add non-obsolete resource
    ResourceFactory.create(project=project, obsolete=False)

    response = client_superuser.get(url)
    assert response.status_code == 200
    assert translate_url.encode() in response.content


@pytest.mark.django_db
def test_project_add_locale(client_superuser):
    locale_kl = LocaleFactory.create(code="kl", name="Klingon")
    locale_gs = LocaleFactory.create(code="gs", name="Geonosian")
    project = ProjectFactory.create(locales=[locale_kl])

    url = reverse("pontoon.admin.project", args=(project.slug,))

    # Boring data creation for FormSets. Django is painful with that,
    # or I don't know how to handle that more gracefully.
    form = ProjectForm(instance=project)
    form_data = dict(form.initial)
    del form_data["deadline"]
    del form_data["contact"]
    form_data.update(
        {
            "externalresource_set-TOTAL_FORMS": "1",
            "externalresource_set-MAX_NUM_FORMS": "1000",
            "externalresource_set-MIN_NUM_FORMS": "0",
            "externalresource_set-INITIAL_FORMS": "0",
            "tags-TOTAL_FORMS": "1",
            "tags-INITIAL_FORMS": "0",
            "tags-MAX_NUM_FORMS": "1000",
            "tags-MIN_NUM_FORMS": "0",
            **_repository_form_data(project),
            # These are the values that actually matter.
            "pk": project.pk,
            "locales": [locale_kl.id, locale_gs.id],
            "configuration_file": "",
        }
    )

    response = client_superuser.post(url, form_data)
    assert response.status_code == 200
    assert b". Error." not in response.content

    # Verify we have the right ProjectLocale objects.
    pl = ProjectLocale.objects.filter(project=project)
    assert len(pl) == 2


@pytest.mark.django_db
def test_project_form_preselects_pretranslate_locales():
    """ProjectForm must pre-select the pretranslation-enabled locales for an
    existing project, so the (CSS-hidden) locales_pretranslate <select> renders
    with them selected and a save that doesn't touch the pretranslate selector
    doesn't submit an empty value and wipe the flags.
    """
    locale_kl = LocaleFactory.create(code="kl", name="Klingon")
    locale_gs = LocaleFactory.create(code="gs", name="Geonosian")
    project = ProjectFactory.create(locales=[locale_kl, locale_gs])
    ProjectLocale.objects.filter(project=project, locale=locale_kl).update(
        pretranslation_enabled=True
    )

    form = ProjectForm(instance=project)
    # Only the pretranslation-enabled locale must be preselected.
    assert list(form["locales_pretranslate"].value()) == [locale_kl.pk]


@pytest.mark.django_db
def test_manage_project_save_preserves_pretranslate_locales(client_superuser):
    """Saving the project form without resubmitting locales_pretranslate (e.g.
    when only other fields are edited) must not wipe the pretranslation_enabled
    flags of existing ProjectLocales.
    """
    locale_kl = LocaleFactory.create(code="kl", name="Klingon")
    locale_gs = LocaleFactory.create(code="gs", name="Geonosian")
    project = ProjectFactory.create(locales=[locale_kl, locale_gs])
    ProjectLocale.objects.filter(project=project, locale=locale_kl).update(
        pretranslation_enabled=True
    )

    url = reverse("pontoon.admin.project", args=(project.slug,))

    form = ProjectForm(instance=project)
    form_data = dict(form.initial)
    del form_data["deadline"]
    del form_data["contact"]
    form_data.update(
        {
            "externalresource_set-TOTAL_FORMS": "1",
            "externalresource_set-MAX_NUM_FORMS": "1000",
            "externalresource_set-MIN_NUM_FORMS": "0",
            "externalresource_set-INITIAL_FORMS": "0",
            "tags-TOTAL_FORMS": "1",
            "tags-INITIAL_FORMS": "0",
            "tags-MAX_NUM_FORMS": "1000",
            "tags-MIN_NUM_FORMS": "0",
            **_repository_form_data(project),
            "pk": project.pk,
            "locales": [locale_kl.id, locale_gs.id],
            "configuration_file": "",
            # locales_pretranslate is the form value submitted by the (hidden)
            # <select>, which is preselected from the project's enabled locales.
            "locales_pretranslate": [locale_kl.id],
        }
    )

    response = client_superuser.post(url, form_data)
    assert response.status_code == 200
    assert b". Error." not in response.content

    # The pretranslation_enabled flag must still be set for locale_kl.
    pl = ProjectLocale.objects.get(project=project, locale=locale_kl)
    assert pl.pretranslation_enabled is True
