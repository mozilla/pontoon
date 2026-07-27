import warnings

from unittest.mock import patch

import pytest

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.paginator import UnorderedObjectListWarning
from django.http import HttpResponse
from django.shortcuts import render
from django.test import Client

from pontoon.base.models import TranslationMemoryEntry
from pontoon.test.factories import (
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    ProjectLocaleFactory,
    ResourceFactory,
    TranslationFactory,
    UserFactory,
)


def _get_sorted_users():
    return sorted(UserFactory.create_batch(size=3), key=lambda u: u.email)


def _tmx_file_upload(locale_code, entries):
    """
    Build a minimal TMX file with the given (source, target) entries
    """
    units = "".join(
        f'<tu srclang="en-US">'
        f'<tuv xml:lang="en-US"><seg>{source}</seg></tuv>'
        f'<tuv xml:lang="{locale_code}"><seg>{target}</seg></tuv>'
        f"</tu>"
        for source, target in entries
    )
    content = (
        '<?xml version="1.0" encoding="UTF-8"?>'
        '<tmx version="1.4"><header srclang="en-US"/>'
        f"<body>{units}</body></tmx>"
    ).encode("utf-8")
    return SimpleUploadedFile("upload.tmx", content, content_type="application/xml")


@pytest.fixture
def translators():
    return _get_sorted_users()


@pytest.fixture
def managers():
    return _get_sorted_users()


@pytest.mark.no_cover
@pytest.mark.django_db
def test_teams_list(client, locale_a):
    """
    Tests if the teams list is rendered properly.
    """
    response = client.get("/teams/")
    assert response.status_code == 200
    assert response.resolver_match.view_name == "pontoon.teams"


@pytest.mark.django_db
def test_missing_locale(client):
    """
    Tests if the backend is returning an error on the missing locale.
    """
    response = client.get("/missing-locale/")

    assert response.status_code == 404
    assert response.resolver_match.view_name == "pontoon.teams.team"


@pytest.mark.django_db
@patch("pontoon.teams.views.render", wraps=render)
def test_locale_view(mock_render, translation_a, client):
    """
    Check if the locale view finds the right locale and passes it to the template.
    """
    client.get(f"/{translation_a.locale.code}/")

    assert mock_render.call_args[0][2]["locale"] == translation_a.locale


@pytest.mark.django_db
def test_contributors_of_missing_locale(client):
    """
    Tests if the contributors view is returning an error on the missing locale.
    """
    response = client.get("/missing-locale/contributors/")

    assert response.status_code == 404
    assert response.resolver_match.view_name == "pontoon.teams.contributors"


@pytest.mark.django_db
@patch("pontoon.teams.views.render", wraps=render)
def test_ajax_permissions_locale_translators_managers_order(
    render_mock,
    admin_client,
    locale_a,
    translators,
    managers,
):
    """
    Translators and managers of a locale should be sorted by email in
    "Permissions" tab.
    """
    locale_a.translators_group.user_set.add(*translators)
    locale_a.managers_group.user_set.add(*managers)

    admin_client.get("/%s/ajax/permissions/" % locale_a.code)
    response_context = render_mock.call_args[0][2]

    assert list(response_context["translators"]) == translators
    assert list(response_context["managers"]) == managers


@pytest.mark.django_db
@patch("pontoon.teams.views.render", wraps=render)
def test_ajax_permissions_project_locale_translators_order(
    render_mock,
    admin_client,
    locale_a,
    project_locale_a,
    resource_a,  # required for project_locale_a to work
    translators,
):
    """
    Translators and managers of a locale should be sorted by email in
    "Permissions" tab.
    """
    project_locale_a.translators_group.user_set.add(*translators)
    project_locale_a.has_custom_translators = True
    project_locale_a.save()

    admin_client.get("/%s/ajax/permissions/" % locale_a.code)
    response_context = render_mock.call_args[0][2]
    project_locales = response_context["project_locales"]

    # Check project_locale id in the permissions form
    assert project_locales[0].pk == project_locale_a.pk

    # Check project_locale translators
    assert len(project_locales[0].translators) == len(translators)
    assert project_locales[0].translators[0].pk == translators[0].pk
    assert project_locales[0].translators[0].email == translators[0].email
    assert project_locales[0].translators[0].first_name == translators[0].first_name
    assert project_locales[0].translators[1].pk == translators[1].pk
    assert project_locales[0].translators[1].email == translators[1].email
    assert project_locales[0].translators[1].first_name == translators[1].first_name
    assert project_locales[0].translators[2].pk == translators[2].pk
    assert project_locales[0].translators[2].email == translators[2].email
    assert project_locales[0].translators[2].first_name == translators[2].first_name


@pytest.mark.django_db
def test_users_permissions_for_ajax_permissions_view(
    client,
    locale_a,
    member,
):
    """
    Check if anonymous users and users without permissions can't access
    Permissions Tab.
    """

    response = client.get(f"/{locale_a.code}/ajax/permissions/")
    assert response.status_code == 403
    assert b"<title>Forbidden page</title>" in response.content

    # Check if users without permissions for the locale can get this tab.
    response = member.client.get(f"/{locale_a.code}/ajax/permissions/")
    assert response.status_code == 403
    assert b"<title>Forbidden page</title>" in response.content

    locale_a.managers_group.user_set.add(member.user)

    # Bump up permissions for user0 and check if the view is accessible.
    response = member.client.get(f"/{locale_a.code}/ajax/permissions/")
    assert response.status_code == 200
    assert b"<title>Forbidden page</title>" not in response.content

    # Remove permissions for user0 and check if the view is not accessible.
    locale_a.managers_group.user_set.clear()

    response = member.client.get(f"/{locale_a.code}/ajax/permissions/")
    assert response.status_code == 403
    assert b"<title>Forbidden page</title>" in response.content

    # All unauthorized attempts to POST data should be blocked
    response = member.client.post(
        f"/{locale_a.code}/ajax/permissions/",
        data={"smth": "smth"},
    )
    assert response.status_code == 403
    assert b"<title>Forbidden page</title>" in response.content

    response = client.post(
        f"/{locale_a.code}/ajax/permissions/",
        data={"smth": "smth"},
    )
    assert response.status_code == 403
    assert b"<title>Forbidden page</title>" in response.content


@pytest.mark.django_db
@patch(
    "pontoon.teams.views.LocaleContributorsView.render_to_response",
    return_value=HttpResponse(""),
)
def test_locale_top_contributors(mock_render, client, translation_a, locale_b):
    """
    Tests if the view returns top contributors specific for given locale.
    """
    client.get(
        f"/{translation_a.locale.code}/ajax/contributors/",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    response_context = mock_render.call_args[0][0]
    assert response_context["locale"] == translation_a.locale
    assert list(response_context["contributors"]) == [translation_a.user]

    client.get(
        f"/{locale_b.code}/ajax/contributors/",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    response_context = mock_render.call_args[0][0]
    assert response_context["locale"] == locale_b
    assert list(response_context["contributors"]) == []


@pytest.mark.django_db
def test_ajax_projects_request_more_projects_button_visibility(
    member,
    managers,
):
    locale_a = LocaleFactory.create(code="thl", name="Klingon")
    project_a = ProjectFactory.create(
        name="Project A", slug="project-a", can_be_requested=False
    )
    project_b = ProjectFactory.create(
        name="Project B", slug="project-b", can_be_requested=True
    )
    ProjectLocaleFactory.create(project=project_a, locale=locale_a)

    resource_a = ResourceFactory.create(project=project_a)
    ResourceFactory.create(project=project_b)

    entity_a = EntityFactory.create(resource=resource_a)

    locale_a.managers_group.user_set.add(*managers)

    response = member.client.get(
        f"/{locale_a.code}/ajax/",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    assert response.status_code == 200
    assert b"request-projects" not in response.content

    for manager in managers:
        locale_a.managers_group.user_set.remove(manager)

    response = member.client.get(
        f"/{locale_a.code}/ajax/",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    assert response.status_code == 200
    assert b"request-projects" in response.content

    locale_a.managers_group.user_set.add(*managers)
    TranslationFactory.create(
        entity=entity_a, locale=locale_a, user=member.user, approved=True
    )

    response = member.client.get(
        f"/{locale_a.code}/ajax/",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    assert response.status_code == 200
    assert b"request-projects" in response.content


@pytest.mark.django_db
def test_ajax_translation_memory_entries_are_ordered(member, locale_a):
    """
    Regression test: the TM tab queryset must be ordered before pagination,
    otherwise Paginator emits UnorderedObjectListWarning.
    """
    locale_a.translators_group.user_set.add(member.user)

    TranslationMemoryEntry.objects.create(
        locale=locale_a,
        source="Source B",
        target="Target B",
    )
    TranslationMemoryEntry.objects.create(
        locale=locale_a,
        source="Source A",
        target="Target A",
    )

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")

        response = member.client.get(
            f"/{locale_a.code}/ajax/translation-memory/",
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )

    assert response.status_code == 200
    assert not any(
        issubclass(warning.category, UnorderedObjectListWarning) for warning in caught
    )


@pytest.mark.django_db
def test_ajax_translation_memory_requires_ajax(member, locale_a):
    response = member.client.get(f"/{locale_a.code}/ajax/translation-memory/")

    assert response.status_code == 400
    assert response.content == b"Bad Request: Request must be AJAX"


@pytest.mark.django_db
@patch("pontoon.teams.views.render", wraps=render)
def test_ajax_translation_memory_grouping_and_count(render_mock, member, locale_a):
    locale_a.translators_group.user_set.add(member.user)

    TranslationMemoryEntry.objects.create(
        locale=locale_a,
        source="Shared source",
        target="Shared target",
    )
    TranslationMemoryEntry.objects.create(
        locale=locale_a,
        source="Shared source",
        target="Shared target",
    )

    response = member.client.get(
        f"/{locale_a.code}/ajax/translation-memory/",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    response_context = render_mock.call_args[0][2]
    tm_entries = response_context["tm_entries"]

    assert response.status_code == 200
    assert len(tm_entries) == 1
    assert tm_entries[0]["source"] == "Shared source"
    assert tm_entries[0]["target"] == "Shared target"
    assert tm_entries[0]["count"] == 2
    assert response.content.count(b"Shared source") == 1
    assert b"Delete 2 TM" in response.content


@pytest.mark.django_db
@patch("pontoon.teams.views.render", wraps=render)
def test_ajax_translation_memory_search_filters_source_and_target(
    render_mock,
    member,
    locale_a,
):
    locale_a.translators_group.user_set.add(member.user)

    source_match = TranslationMemoryEntry.objects.create(
        locale=locale_a,
        source="Source search needle",
        target="First translation",
    )
    target_match = TranslationMemoryEntry.objects.create(
        locale=locale_a,
        source="Second entry",
        target="Target search needle",
    )
    TranslationMemoryEntry.objects.create(
        locale=locale_a,
        source="Unrelated entry",
        target="Other translation",
    )

    response = member.client.get(
        f"/{locale_a.code}/ajax/translation-memory/",
        {"search": "source search"},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    response_context = render_mock.call_args[0][2]

    assert response.status_code == 200
    assert list(response_context["tm_entries"]) == [
        {
            "source": source_match.source,
            "target": source_match.target,
            "count": 1,
            "ids": [source_match.id],
            "entity_ids": None,
        }
    ]

    render_mock.reset_mock()
    response = member.client.get(
        f"/{locale_a.code}/ajax/translation-memory/",
        {"search": "target search"},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    response_context = render_mock.call_args[0][2]

    assert response.status_code == 200
    assert list(response_context["tm_entries"]) == [
        {
            "source": target_match.source,
            "target": target_match.target,
            "count": 1,
            "ids": [target_match.id],
            "entity_ids": None,
        }
    ]


@pytest.mark.django_db
def test_ajax_translation_memory_invalid_page_params_return_400(member, locale_a):
    locale_a.translators_group.user_set.add(member.user)

    response = member.client.get(
        f"/{locale_a.code}/ajax/translation-memory/",
        {"page": "abc"},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    assert response.status_code == 400
    assert response.json()["message"].startswith("Bad Request:")

    response = member.client.get(
        f"/{locale_a.code}/ajax/translation-memory/",
        {"pages": "abc"},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    assert response.status_code == 400
    assert response.json()["message"].startswith("Bad Request:")


@pytest.mark.django_db
@patch("pontoon.teams.views.render", wraps=render)
def test_ajax_translation_memory_locale_isolation(
    render_mock,
    member,
    locale_a,
    locale_b,
):
    locale_a.translators_group.user_set.add(member.user)

    TranslationMemoryEntry.objects.create(
        locale=locale_a,
        source="Locale A source",
        target="Locale A target",
    )
    TranslationMemoryEntry.objects.create(
        locale=locale_b,
        source="Locale B source",
        target="Locale B target",
    )

    response = member.client.get(
        f"/{locale_a.code}/ajax/translation-memory/",
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    response_context = render_mock.call_args[0][2]

    assert response.status_code == 200
    assert [entry["source"] for entry in response_context["tm_entries"]] == [
        "Locale A source"
    ]
    assert b"Locale A source" in response.content
    assert b"Locale B source" not in response.content


@pytest.mark.django_db
def test_ajax_translation_memory_edit_requires_permission(member, locale_a):
    url = f"/{locale_a.code}/ajax/translation-memory/edit/"
    tm_entry = TranslationMemoryEntry.objects.create(
        locale=locale_a,
        source="Source",
        target="Target",
    )
    data = {"ids[]": [tm_entry.id], "target": "Edited target"}

    response = Client().post(
        url,
        data,
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert response.status_code == 403

    response = member.client.post(
        url,
        data,
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert response.status_code == 403

    locale_a.translators_group.user_set.add(member.user)
    response = member.client.post(
        url,
        {"ids[]": [tm_entry.id]},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert response.status_code == 400
    assert response.json()["message"] == "Bad Request: 'target'"


@pytest.mark.django_db
def test_ajax_translation_memory_edit_scoped_to_locale(member, locale_a, locale_b):
    locale_a.translators_group.user_set.add(member.user)
    locale_b_entry = TranslationMemoryEntry.objects.create(
        locale=locale_b,
        source="Locale B source",
        target="Locale B target",
    )

    response = member.client.post(
        f"/{locale_a.code}/ajax/translation-memory/edit/",
        {"ids[]": [locale_b_entry.id], "target": "Edited target"},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    assert response.status_code == 200
    locale_b_entry.refresh_from_db()
    assert locale_b_entry.target == "Locale B target"


@pytest.mark.django_db
def test_ajax_translation_memory_delete_requires_permission(member, locale_a):
    url = f"/{locale_a.code}/ajax/translation-memory/delete/"
    tm_entry = TranslationMemoryEntry.objects.create(
        locale=locale_a,
        source="Source",
        target="Target",
    )
    data = {"ids[]": [tm_entry.id]}

    response = Client().post(
        url,
        data,
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert response.status_code == 403

    response = member.client.post(
        url,
        data,
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert response.status_code == 403


@pytest.mark.django_db
def test_ajax_translation_memory_delete_scoped_to_locale(member, locale_a, locale_b):
    locale_a.translators_group.user_set.add(member.user)
    locale_b_entry = TranslationMemoryEntry.objects.create(
        locale=locale_b,
        source="Locale B source",
        target="Locale B target",
    )

    response = member.client.post(
        f"/{locale_a.code}/ajax/translation-memory/delete/",
        {"ids[]": [locale_b_entry.id]},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    assert response.status_code == 200
    assert TranslationMemoryEntry.objects.filter(pk=locale_b_entry.pk).count() == 1


@pytest.mark.django_db
def test_ajax_translation_memory_upload_requires_permission(member, locale_a):
    url = f"/{locale_a.code}/ajax/translation-memory/upload/"
    data = {"tmx_file": _tmx_file_upload(locale_a.code, [("Source", "Target")])}

    response = Client().post(url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert response.status_code == 403
    response = member.client.post(url, data, HTTP_X_REQUESTED_WITH="XMLHttpRequest")
    assert response.status_code == 403

    assert TranslationMemoryEntry.objects.filter(locale=locale_a).count() == 0


@pytest.mark.django_db
def test_ajax_translation_memory_upload_rejects_non_tmx_file(member, locale_a):
    locale_a.translators_group.user_set.add(member.user)

    response = member.client.post(
        f"/{locale_a.code}/ajax/translation-memory/upload/",
        {"tmx_file": SimpleUploadedFile("upload.txt", b"blah", "text/plain")},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    assert response.status_code == 400
    assert response.json()["status"] is False
    assert TranslationMemoryEntry.objects.filter(locale=locale_a).count() == 0


@pytest.mark.django_db
def test_ajax_translation_memory_upload_creates_entries_scoped_to_locale(
    member,
    locale_a,
    locale_b,
):
    locale_a.translators_group.user_set.add(member.user)

    response = member.client.post(
        f"/{locale_a.code}/ajax/translation-memory/upload/",
        {
            "tmx_file": _tmx_file_upload(
                locale_a.code,
                [("Source one", "Target one"), ("Source two", "Target two")],
            )
        },
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["status"] is True
    assert body["imported"] == 2

    # Entries are created for the locale in the URL only.
    assert set(
        TranslationMemoryEntry.objects.filter(locale=locale_a).values_list(
            "source", "target"
        )
    ) == {("Source one", "Target one"), ("Source two", "Target two")}
    assert TranslationMemoryEntry.objects.filter(locale=locale_b).count() == 0


@pytest.mark.django_db
def test_ajax_translation_memory_upload_skips_duplicates(member, locale_a):
    locale_a.translators_group.user_set.add(member.user)
    TranslationMemoryEntry.objects.create(
        locale=locale_a,
        source="Existing source",
        target="Existing target",
    )

    response = member.client.post(
        f"/{locale_a.code}/ajax/translation-memory/upload/",
        {
            "tmx_file": _tmx_file_upload(
                locale_a.code,
                [
                    ("Existing source", "Existing target"),
                    ("Fresh source", "Fresh target"),
                ],
            )
        },
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    assert response.status_code == 200
    body = response.json()
    assert body["imported"] == 1
    assert body["duplicates"] == 1
    assert TranslationMemoryEntry.objects.filter(locale=locale_a).count() == 2
