import pytest

from django.urls import reverse

from pontoon.administration.forms import ProjectForm
from pontoon.base.models import ProjectLocale
from pontoon.test.factories import (
    LocaleFactory,
    ProjectFactory,
    ResourceFactory,
)


@pytest.mark.django_db
def test_manage_project(client_superuser):
    url = reverse("pontoon.admin.project.new")
    response = client_superuser.get(url)
    assert response.status_code == 200


@pytest.mark.django_db
def test_manage_project_translate_link_excludes_obsolete_resources(client_superuser):
    """Test that Translate link is only shown when non-obsolete resources exist."""
    locale_kl = LocaleFactory.create(code="tlh", name="Klingon")
    project = ProjectFactory.create(
        locales=[locale_kl],
        repositories=[],
    )

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
    project = ProjectFactory.create(
        locales=[locale_kl],
        repositories=[],
    )

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
            "repositories-INITIAL_FORMS": "0",
            "repositories-MIN_NUM_FORMS": "0",
            "repositories-MAX_NUM_FORMS": "1000",
            "repositories-TOTAL_FORMS": "0",
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
    project = ProjectFactory.create(
        locales=[locale_kl, locale_gs],
        repositories=[],
    )
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
    project = ProjectFactory.create(
        locales=[locale_kl, locale_gs],
        repositories=[],
    )
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
            "repositories-INITIAL_FORMS": "0",
            "repositories-MIN_NUM_FORMS": "0",
            "repositories-MAX_NUM_FORMS": "1000",
            "repositories-TOTAL_FORMS": "0",
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
