import pytest

from django.urls import reverse


@pytest.fixture
def search_url():
    return reverse("pontoon.search")


@pytest.mark.django_db
def test_search_options_no_active_search_uses_profile_defaults(
    member, locale_a, search_url
):
    """Without an active search, checkboxes reflect the user's profile settings."""
    member.user.profile.search_identifiers = True
    member.user.profile.search_match_case = True
    member.user.profile.search_match_whole_word = True
    member.user.profile.save()

    response = member.client.get(search_url, {"locale": locale_a.code})
    assert response.status_code == 200
    content = response.content.decode()
    assert "search-identifiers-enabled enabled" in content
    assert "match-case-enabled enabled" in content
    assert "match-whole-word-enabled enabled" in content


@pytest.mark.django_db
def test_search_options_with_active_search_uses_global_defaults(
    member, locale_a, search_url
):
    """With an active search but no explicit option params, checkboxes use global
    defaults (False) so the UI reflects the actual settings used for that search."""
    member.user.profile.search_identifiers = True
    member.user.profile.search_match_case = True
    member.user.profile.search_match_whole_word = True
    member.user.profile.save()

    response = member.client.get(
        search_url, {"search": "badge-new", "locale": locale_a.code}
    )
    assert response.status_code == 200
    content = response.content.decode()
    assert "search-identifiers-enabled enabled" not in content
    assert "match-case-enabled enabled" not in content
    assert "match-whole-word-enabled enabled" not in content


@pytest.mark.django_db
def test_search_options_explicit_url_params_override_profile(
    member, locale_a, search_url
):
    """Explicit URL params always take precedence over profile defaults."""
    member.user.profile.search_identifiers = False
    member.user.profile.search_match_case = False
    member.user.profile.search_match_whole_word = False
    member.user.profile.save()

    response = member.client.get(
        search_url,
        {
            "search": "badge-new",
            "locale": locale_a.code,
            "search_identifiers": "true",
            "search_match_case": "true",
            "search_match_whole_word": "true",
        },
    )
    assert response.status_code == 200
    content = response.content.decode()
    assert "search-identifiers-enabled enabled" in content
    assert "match-case-enabled enabled" in content
    assert "match-whole-word-enabled enabled" in content
