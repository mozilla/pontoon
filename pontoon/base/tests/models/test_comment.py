import pytest

from pontoon.test.factories import TeamCommentFactory, TranslationCommentFactory


@pytest.mark.django_db
def test_serialize_comments():
    tr = TranslationCommentFactory.create()
    team = TeamCommentFactory.create()

    assert tr.serialize() == {
        "author": tr.author.name_or_email,
        "username": tr.author.username,
        "user_status": tr.author.status(tr.translation.locale),
        "user_gravatar_url_small": tr.author.gravatar_url(88),
        "created_at": tr.timestamp.strftime("%b %d, %Y %H:%M"),
        "date_iso": tr.timestamp.isoformat(),
        "content": tr.content,
        "pinned": tr.pinned,
        "id": tr.id,
    }

    assert team.serialize() == {
        "author": team.author.name_or_email,
        "username": team.author.username,
        "user_status": team.author.status(team.locale),
        "user_gravatar_url_small": team.author.gravatar_url(88),
        "created_at": team.timestamp.strftime("%b %d, %Y %H:%M"),
        "date_iso": team.timestamp.isoformat(),
        "content": team.content,
        "pinned": team.pinned,
        "id": team.id,
    }
