import pytest

from django.contrib.auth.models import AnonymousUser
from django.template.loader import get_template


@pytest.mark.django_db
def test_disabled_account_contact(settings, rf):
    settings.DEFAULT_FROM_EMAIL = "Pontoon <no-reply@example.org>"
    settings.CONTACT_EMAIL = "team@example.org"
    request = rf.get("/accounts/inactive/")
    request.user = AnonymousUser()
    html = get_template("account/account_inactive.html").render(
        {"settings": settings}, request=request
    )
    assert 'href="mailto:team@example.org"' in html
    assert "no-reply@example.org" not in html
