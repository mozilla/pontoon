from unittest.mock import patch

import pytest

from django.test.client import RequestFactory

from pontoon.messaging.emails import send_verification_email


@pytest.mark.django_db
def test_send_verification_email(member):
    with patch("pontoon.messaging.emails.EmailMultiAlternatives") as mock_email_message:
        rf = RequestFactory()
        request = rf.get("/settings/")
        request.user = member.user

        link = "EMAIL-VERIFICATION-LINK"
        send_verification_email(request.user, link)
        assert mock_email_message.called

        kwargs = mock_email_message.call_args.kwargs
        assert link in kwargs["body"]
        assert kwargs["to"] == [request.user.email]
