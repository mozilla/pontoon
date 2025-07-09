from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from django.contrib.auth.models import User


class PersonalAccessTokenAuthentication(BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get("Authorization")

        if not auth_header or not auth_header.startswith("Bearer "):
            raise AuthenticationFailed(
                {"detail": "Missing or invalid Authorization header"}
            )

        token = auth_header.split(" ")[1]

        if token != "abc":
            raise AuthenticationFailed({"detail": "Invalid token"})

        try:
            user = User.objects.get(username="pontoon")
        except User.DoesNotExist:
            raise AuthenticationFailed({"detail": "User not found"})

        return (user, None)

    # create the token model, api endpoints to create, revoke, edit tokens
    # create the UI to add, delete tokens in user settings
    # create token expiration, repeated wrong tries
