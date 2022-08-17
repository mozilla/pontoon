import pytest

from unittest.mock import patch

from django.test.client import RequestFactory

from pontoon.base.models import User
from pontoon.contributors.utils import (
    generate_verification_token,
    send_verification_email,
    check_verification_token,
)


@pytest.mark.django_db
def test_generate_verification_token(member):
    with patch("jwt.encode") as mock_encode:
        generate_verification_token(member.user)
        assert mock_encode.called

        args = mock_encode.call_args.args
        assert list(args[0].values())[0] == member.user.pk
        assert list(args[0].values())[1] == member.user.profile.contact_email


@pytest.mark.django_db
def test_send_verification_email(member):
    with patch("pontoon.contributors.utils.EmailMessage") as mock_email_message:
        rf = RequestFactory()
        request = rf.get("/settings/")
        request.user = member.user

        token = "EMAIL-VERIFICATION-TOKEN"
        send_verification_email(request, token)
        assert mock_email_message.called

        kwargs = mock_email_message.call_args.kwargs
        assert token in kwargs["body"]
        assert kwargs["to"] == [None]


@pytest.mark.django_db
def test_check_verification_token(member, user_b):
    # Invalid token
    token = "INVALID-VERIFICATION-TOKEN"
    title, message = check_verification_token(member.user, token)
    assert title == "Oops!"
    assert message == "Invalid verification token"
    assert User.objects.get(pk=member.user.pk).profile.contact_email_verified is False

    # Valid token
    token = generate_verification_token(member.user)
    title, message = check_verification_token(member.user, token)
    assert title == "Success!"
    assert message == "Your email address has been verified"
    assert User.objects.get(pk=member.user.pk).profile.contact_email_verified is True

    # Invalid user
    token = generate_verification_token(user_b)
    title, message = check_verification_token(member.user, token)
    assert title == "Oops!"
    assert message == "Invalid verification token"
