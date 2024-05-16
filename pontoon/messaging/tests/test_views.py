import pytest

from pontoon.base.models import User


@pytest.mark.django_db
def test_dismiss_email_consent(member):
    """Test if dismiss_email_consent view works and fails as expected."""
    params = {}
    response = member.client.post(f"/dismiss-email-consent/", params)
    assert response.status_code == 400
    assert response.json()["message"] == "Bad Request: Value not set"

    params = {
        "value": "false",
    }
    response = member.client.post(f"/dismiss-email-consent/", params)
    profile = User.objects.get(pk=member.user.pk).profile
    assert profile.email_communications_enabled is False
    assert profile.email_consent_dismissed_at is not None
    assert response.status_code == 200
    assert response.json()["next"] == "/"

    params = {
        "value": "true",
    }
    response = member.client.post(f"/dismiss-email-consent/", params)
    profile = User.objects.get(pk=member.user.pk).profile
    assert profile.email_communications_enabled is True
    assert profile.email_consent_dismissed_at is not None
    assert response.status_code == 200
    assert response.json()["next"] == "/"
