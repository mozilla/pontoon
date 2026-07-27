"""Central registry of Pontoon's built-in system users.

System users are marked with `UserProfile.system_user`, which makes it possible
to identify bot accounts and exclude them from specific features (leaderboards,
notifications, etc.).

This module defines which system user is used for each purpose and provides
helper functions to retrieve them.

Code that needs a specific system user should use these functions rather than
looking one up directly, so that the lookup logic lives in a single place.
"""

from typing import Literal

from django.contrib.auth.models import User


PretranslationAuthor = Literal["gt", "tm"]

SYNC = "pontoon-sync"
GOOGLE_TRANSLATE = "google-translate"
TRANSLATION_MEMORY = "translation-memory"

# Keyed by the short codes used by pretranslation ("gt", "tm").
PRETRANSLATION_AUTHORS: dict[PretranslationAuthor, str] = {
    "tm": TRANSLATION_MEMORY,
    "gt": GOOGLE_TRANSLATE,
}

# Every known system user. Not consumed directly by application code, but
# used by tests to make sure every account here exists and is flagged.
ALL: tuple[str, ...] = (SYNC, GOOGLE_TRANSLATE, TRANSLATION_MEMORY)


def get_sync_user() -> User:
    """The user that VCS sync attributes its actions to."""
    return User.objects.get(username=SYNC)


def get_pretranslation_authors() -> dict[PretranslationAuthor, User]:
    """Pretranslation authors, keyed by the short codes in PRETRANSLATION_AUTHORS."""
    users_by_username = {
        user.username: user
        for user in User.objects.filter(username__in=PRETRANSLATION_AUTHORS.values())
    }
    return {
        key: users_by_username[username]
        for key, username in PRETRANSLATION_AUTHORS.items()
    }
