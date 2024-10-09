import time

import pytest

from django.test import Client, TestCase, override_settings
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


class ThrottleIpMiddlewareTest(TestCase):
    def setUp(self):
        self.client = Client()

    @override_settings(THROTTLE_MAX_COUNT=5)
    @override_settings(THROTTLE_BLOCK_DURATION=60)
    def test_throttle_limit_reached(self):
        """Test that requests are throttled after the limit is reached."""
        url = "/"

        # Make 5 requests within the limit
        for _ in range(5):
            response = self.client.get(url, REMOTE_ADDR="192.168.0.1")
            self.assertEqual(response.status_code, 200)

        # 6th request should be throttled
        response = self.client.get(url, REMOTE_ADDR="192.168.0.1")
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.json(), {"detail": "Too Many Requests"})

        # Check that the IP remains blocked for the block duration
        response = self.client.get(url, REMOTE_ADDR="192.168.0.1")
        self.assertEqual(response.status_code, 429)

    @override_settings(THROTTLE_MAX_COUNT=5)
    @override_settings(THROTTLE_BLOCK_DURATION=2)
    def test_throttle_reset_after_block_duration(self):
        """Test that requests are allowed after the block duration expires."""
        url = "/"

        # Make 5 requests within the limit
        for _ in range(5):
            response = self.client.get(url, REMOTE_ADDR="192.168.0.2")
            self.assertEqual(response.status_code, 200)

        # 6th request should be throttled
        response = self.client.get(url, REMOTE_ADDR="192.168.0.2")
        self.assertEqual(response.status_code, 429)

        # Wait for block duration to pass
        time.sleep(3)

        # Make another request after block duration
        response = self.client.get(url, REMOTE_ADDR="192.168.0.2")
        self.assertEqual(response.status_code, 200)

    @override_settings(THROTTLE_MAX_COUNT=5)
    @override_settings(THROTTLE_BLOCK_DURATION=60)
    def test_throttle_with_different_ips(self):
        """Test that throttling is applied separately for different IPs."""
        url = "/"

        # Make 5 requests from IP1
        for _ in range(5):
            response = self.client.get(url, REMOTE_ADDR="192.168.0.3")
            self.assertEqual(response.status_code, 200)

        # 6th request from IP1 should be throttled
        response = self.client.get(url, REMOTE_ADDR="192.168.0.3")
        self.assertEqual(response.status_code, 429)

        # Requests from IP2 should not be throttled
        response = self.client.get(url, REMOTE_ADDR="192.168.0.4")
        self.assertEqual(response.status_code, 200)
