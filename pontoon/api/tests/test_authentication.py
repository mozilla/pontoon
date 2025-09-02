import pytest

from rest_framework.exceptions import AuthenticationFailed

from django.contrib.auth.hashers import make_password
from django.utils.timezone import now, timedelta

from pontoon.api.authentication import PersonalAccessTokenAuthentication
from pontoon.api.models import PersonalAccessToken


@pytest.mark.django_db
def test_authenticate_valid_token(member):
    token = PersonalAccessToken.objects.create(
        user=member.user,
        name="Test Token 1",
        token_hash="hashed_token",
        expires_at=now() + timedelta(days=1),
    )
    token_id = token.id
    token_unhashed = "unhashed-token"
    token.token_hash = make_password(token_unhashed)
    token.save()

    auth = PersonalAccessTokenAuthentication()
    request = type(
        "Request",
        (),
        {"headers": {"Authorization": f"Bearer {token_id}_{token_unhashed}"}},
    )

    authenticated_user, _ = auth.authenticate(request)
    assert authenticated_user == member.user


@pytest.mark.django_db
def test_authenticate_missing_authorization_header():
    auth = PersonalAccessTokenAuthentication()
    request = type("Request", (), {"headers": {}})

    with pytest.raises(AuthenticationFailed) as excinfo:
        auth.authenticate(request)
    assert excinfo.value.detail["detail"] == "Missing or invalid Authorization header."


@pytest.mark.django_db
def test_authenticate_malformed_token_format():
    auth = PersonalAccessTokenAuthentication()
    request = type(
        "Request", (), {"headers": {"Authorization": "Bearer malformed_token"}}
    )

    with pytest.raises(AuthenticationFailed) as excinfo:
        auth.authenticate(request)
    assert excinfo.value.detail["detail"] == "Malformed token format."


@pytest.mark.django_db
def test_authenticate_invalid_token_id():
    auth = PersonalAccessTokenAuthentication()
    request = type(
        "Request", (), {"headers": {"Authorization": "Bearer 999_invalidtoken"}}
    )

    with pytest.raises(AuthenticationFailed) as excinfo:
        auth.authenticate(request)
    assert excinfo.value.detail["detail"] == "Invalid token."


@pytest.mark.django_db
def test_authenticate_invalid_token_hash(member):
    token = PersonalAccessToken.objects.create(
        user=member.user,
        name="Test Token 2",
        token_hash="hashed_token",
        expires_at=now() + timedelta(days=1),
    )
    token_id = token.id
    token_unhashed = "unhashed-token"
    token.token_hash = make_password(token_unhashed)
    token.save()

    auth = PersonalAccessTokenAuthentication()
    request = type(
        "Request", (), {"headers": {"Authorization": f"Bearer {token_id}_wrongtoken"}}
    )

    with pytest.raises(AuthenticationFailed) as excinfo:
        auth.authenticate(request)
    assert excinfo.value.detail["detail"] == "Invalid token."


@pytest.mark.django_db
def test_authenticate_revoked_token(member):
    token = PersonalAccessToken.objects.create(
        user=member.user,
        name="Test Token 2",
        token_hash="hashed_token",
        expires_at=now() + timedelta(days=1),
        revoked=True,
    )
    token_id = token.id
    token_unhashed = "unhashed-token"
    token.token_hash = make_password(token_unhashed)
    token.save()

    auth = PersonalAccessTokenAuthentication()
    request = type(
        "Request",
        (),
        {"headers": {"Authorization": f"Bearer {token_id}_{token_unhashed}"}},
    )

    with pytest.raises(AuthenticationFailed) as excinfo:
        auth.authenticate(request)
    assert excinfo.value.detail["detail"] == "Token has been revoked."


@pytest.mark.django_db
def test_authenticate_expired_token(member):
    token = PersonalAccessToken.objects.create(
        user=member.user,
        name="Test Token 2",
        token_hash="hashed_token",
        expires_at=now() - timedelta(days=1),
    )
    token_id = token.id
    token_unhashed = "unhashed-token"
    token.token_hash = make_password(token_unhashed)
    token.save()
    auth = PersonalAccessTokenAuthentication()
    request = type(
        "Request",
        (),
        {"headers": {"Authorization": f"Bearer {token_id}_{token_unhashed}"}},
    )

    with pytest.raises(AuthenticationFailed) as excinfo:
        auth.authenticate(request)
    assert excinfo.value.detail["detail"] == "Token has expired."
