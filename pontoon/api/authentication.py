from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.permissions import BasePermission

from django.contrib.auth.hashers import check_password
from django.utils import timezone

from pontoon.api.models import PersonalAccessToken


class IsPretranslator(BasePermission):
    def has_permission(self, request, view):
        return request.user.groups.filter(name="pretranslators").exists()


class PersonalAccessTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationFailed(
                {"detail": "Missing or invalid Authorization header."}
            )

        try:
            token_id, unhashed_token = auth_header.split(" ")[1].split("_")
            token_id = int(token_id)
        except (ValueError, TypeError):
            raise AuthenticationFailed({"detail": "Malformed token format."})

        try:
            pat = PersonalAccessToken.objects.get(id=token_id)
        except PersonalAccessToken.DoesNotExist:
            raise AuthenticationFailed({"detail": "Invalid token."})

        if not check_password(unhashed_token, pat.token_hash):
            raise AuthenticationFailed({"detail": "Invalid token."})

        if pat.revoked:
            raise AuthenticationFailed({"detail": "Token has been revoked."})

        if pat.expires_at and pat.expires_at.astimezone() < timezone.now():
            raise AuthenticationFailed({"detail": "Token has expired."})

        pat.last_used = timezone.now()
        pat.save(update_fields=["last_used"])

        user = pat.user
        return (user, None)
