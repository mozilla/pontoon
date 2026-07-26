"""Central registry of Pontoon's built-in system users.

System users are marked with `UserProfile.system_user`, which makes it possible
to identify bot accounts and exclude them from specific features (leaderboards,
notifications, etc.).

This module defines which system user is used for each purpose and provides
helper functions to retrieve them.

Code that needs a specific system user should use these functions rather than
looking one up by email or username, so that the lookup logic lives in a single
place.
"""

from typing import Literal

from django.contrib.auth.models import User


PretranslationAuthor = Literal["gt", "tm"]

SYNC = "pontoon-sync@example.com"
GOOGLE_TRANSLATE = "pontoon-gt@example.com"
TRANSLATION_MEMORY = "pontoon-tm@example.com"

# Keyed by the short codes used by pretranslation ("gt", "tm").
PRETRANSLATION_AUTHORS: dict[PretranslationAuthor, str] = {
    "tm": TRANSLATION_MEMORY,
    "gt": GOOGLE_TRANSLATE,
}

ALL: tuple[str, ...] = (SYNC, GOOGLE_TRANSLATE, TRANSLATION_MEMORY)


def get_sync_user() -> User:
    """The user that VCS sync attributes its actions to."""
    return User.objects.get(email=SYNC)


def get_pretranslation_authors() -> dict[PretranslationAuthor, User]:
    """Pretranslation authors, keyed by the short codes in PRETRANSLATION_AUTHORS."""
    return {
        key: User.objects.get(email=email)
        for key, email in PRETRANSLATION_AUTHORS.items()
    }


def get_pretranslation_user_pks() -> set[int]:
    """Primary keys of the pretranslation authors, for use in QuerySet filters."""
    return set(
        User.objects.filter(email__in=PRETRANSLATION_AUTHORS.values()).values_list(
            "pk", flat=True
        )
    )
