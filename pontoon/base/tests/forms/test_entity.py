import pytest

from pontoon.base.forms import GetEntitiesForm


@pytest.mark.django_db
def test_form_search_with_whitespace():
    form = GetEntitiesForm({"project": "firefox", "locale": "kl", "search": " z"})
    assert form.is_valid()
    assert form.cleaned_data["search"] == " z"
