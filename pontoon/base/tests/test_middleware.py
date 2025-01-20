import time

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


@pytest.mark.django_db
def test_throttle(client, settings):
    """Test that requests are throttled after the limit is reached."""
    settings.THROTTLE_ENABLED = True
    settings.THROTTLE_MAX_COUNT = 5
    settings.THROTTLE_BLOCK_DURATION = 2

    url = reverse("pontoon.homepage")
    ip_address = "192.168.0.1"
    ip_address_2 = "192.168.0.2"

    # Make 5 requests within the limit
    for _ in range(5):
        response = client.get(url, REMOTE_ADDR=ip_address)
        assert response.status_code == 200

    # 6th request should be throttled
    response = client.get(url, REMOTE_ADDR=ip_address)
    assert response.status_code == 429

    # Check that the IP remains blocked for the block duration
    response = client.get(url, REMOTE_ADDR=ip_address)
    assert response.status_code == 429

    # Requests from another IP should not be throttled
    response = client.get(url, REMOTE_ADDR=ip_address_2)
    assert response.status_code == 200

    # Wait for block duration to pass
    time.sleep(settings.THROTTLE_BLOCK_DURATION)

    # Make another request after block duration
    response = client.get(url, REMOTE_ADDR=ip_address)
    assert response.status_code == 200


@pytest.mark.django_db
def test_AccountDisabledMiddleware(client, member, settings):
    # Ensure the user is authenticated but not active
    member.user.is_authenticated = True
    member.user.is_active = False
    member.user.save()

    response = member.client.get("/")
    assert response.status_code == 403
    assert "account_disabled.html" in [t.name for t in response.templates]

    # Ensure the user is authenticated and active
    member.user.is_active = True
    member.user.save()

    response = member.client.get("/")
    assert response.status_code == 200
