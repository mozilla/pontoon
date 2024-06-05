import pytest

from django.urls import reverse
from django.utils import timezone


@pytest.mark.django_db
def test_EmailConsentMiddleware(client, member, settings):
    # By default, Email consent page is disabled
    response = member.client.get("/")
    assert response.status_code == 200

    # If Email consent page is enabled, redirect any view to it
    settings.EMAIL_CONSENT_ENABLED = True
    response = member.client.get("/")
    assert response.status_code == 302

    # Unless that view is the Email consent page itself
    response = member.client.get(reverse("pontoon.messaging.email_consent"))
    assert response.status_code == 200

    # Or the request is AJAX
    response = member.client.get("/", headers={"x-requested-with": "XMLHttpRequest"})
    assert response.status_code == 200

    # Or the user has already dismissed the Email consent
    profile = member.user.profile
    profile.email_consent_dismissed_at = timezone.now()
    profile.save()
    response = member.client.get("/")
    assert response.status_code == 200
