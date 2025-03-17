import pytest

from pontoon.test.factories import ProjectFactory


@pytest.mark.django_db
def test_serialize_comments(comment_a, team_comment_a):
    project = ProjectFactory.create()

    assert comment_a.serialize(project.contact) == {
        "author": comment_a.author.name_or_email,
        "username": comment_a.author.username,
        "user_banner": comment_a.author.banner(
            comment_a.translation.locale, project.contact
        ),
        "user_gravatar_url_small": comment_a.author.gravatar_url(88),
        "created_at": comment_a.timestamp.strftime("%b %d, %Y %H:%M"),
        "date_iso": comment_a.timestamp.isoformat(),
        "content": comment_a.content,
        "pinned": comment_a.pinned,
        "id": comment_a.id,
    }

    assert team_comment_a.serialize(project.contact) == {
        "author": team_comment_a.author.name_or_email,
        "username": team_comment_a.author.username,
        "user_banner": team_comment_a.author.banner(
            team_comment_a.locale, project.contact
        ),
        "user_gravatar_url_small": team_comment_a.author.gravatar_url(88),
        "created_at": team_comment_a.timestamp.strftime("%b %d, %Y %H:%M"),
        "date_iso": team_comment_a.timestamp.isoformat(),
        "content": team_comment_a.content,
        "pinned": team_comment_a.pinned,
        "id": team_comment_a.id,
    }
