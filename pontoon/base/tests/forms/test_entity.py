import pytest

from pontoon.base.forms import GetEntitiesForm


@pytest.mark.django_db
def test_form_search_with_whitespace():
    form = GetEntitiesForm({"project": "firefox", "locale": "kl", "search": " z"})
    assert form.is_valid()
    assert form.cleaned_data["search"] == " z"


@pytest.mark.django_db
def test_form_accepts_created_time():
    form = GetEntitiesForm(
        {
            "project": "firefox",
            "locale": "kl",
            "created_time": "202605240444-202605240444",
        }
    )
    assert form.is_valid()
    assert form.cleaned_data["created_time"] == "202605240444-202605240444"
