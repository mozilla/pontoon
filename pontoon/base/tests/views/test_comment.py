import pytest

from django.contrib.auth.models import Permission
from django.urls import reverse

from pontoon.base.models import Comment
from pontoon.test.factories import TranslationCommentFactory


@pytest.mark.django_db
def test_add_comment(member, translation_a):
    url = reverse("pontoon.add_comment")

    response = member.client.post(
        url,
        {
            "translation": translation_a.pk,
            "entity": translation_a.entity.pk,
            "locale": translation_a.locale.code,
            "comment": "new comment",
        },
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    assert response.status_code == 200

    comment = Comment.objects.get(translation=translation_a, author=member.user)
    assert comment.content == "new comment"


@pytest.mark.django_db
def test_add_comment_sanitizes_html(member, entity_a, locale_a, project_locale_a):
    url = reverse("pontoon.add_comment")

    payload = "<svg><script>alert(1)</script>safe"

    response = member.client.post(
        url,
        {
            "entity": entity_a.pk,
            "locale": locale_a.code,
            "comment": payload,
        },
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    assert response.status_code == 200

    comment = Comment.objects.latest("id")

    assert "<script>" not in comment.content
    assert "safe" in comment.content


@pytest.mark.django_db
def test_pin_comment(member, client, comment_a):
    url = reverse("pontoon.pin_comment")

    # A non-privileged user cannot pin comments
    response = member.client.post(
        url, {"comment_id": comment_a.pk}, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    assert response.status_code == 403

    comment_a.refresh_from_db()
    assert comment_a.pinned is False

    # Grant the user the required permission
    permission = Permission.objects.get(codename="can_manage_project")
    member.user.user_permissions.add(permission)
    member.user.refresh_from_db()

    # The user with can_manage_project permission can pin comments
    response = member.client.post(
        url, {"comment_id": comment_a.pk}, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    assert response.status_code == 200

    comment_a.refresh_from_db()
    assert comment_a.pinned is True


@pytest.mark.django_db
def test_unpin_comment(member, client, team_comment_a):
    url = reverse("pontoon.unpin_comment")
    team_comment_a.pinned = True
    team_comment_a.save()

    # A non-privileged user cannot unpin comments
    response = member.client.post(
        url, {"comment_id": team_comment_a.pk}, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    assert response.status_code == 403

    team_comment_a.refresh_from_db()
    assert team_comment_a.pinned is True

    # Grant the user the required permission
    permission = Permission.objects.get(codename="can_manage_project")
    member.user.user_permissions.add(permission)
    member.user.refresh_from_db()

    # The user with can_manage_project permission can unpin comments
    response = member.client.post(
        url, {"comment_id": team_comment_a.pk}, HTTP_X_REQUESTED_WITH="XMLHttpRequest"
    )
    assert response.status_code == 200

    team_comment_a.refresh_from_db()
    assert team_comment_a.pinned is False


@pytest.mark.django_db
def test_edit_comment(member, comment_a):
    url = reverse("pontoon.edit_comment")

    # A user cannot edit someone else's comment
    response = member.client.post(
        url,
        {"comment_id": comment_a.pk, "content": "edited"},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    assert response.status_code == 403

    # The author can edit their own comment
    comment_a.author = member.user
    comment_a.save()

    response = member.client.post(
        url,
        {"comment_id": comment_a.pk, "content": "edited content"},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    assert response.status_code == 200
    comment_a.refresh_from_db()
    assert comment_a.content == "edited content"


@pytest.mark.django_db
def test_edit_comment_sanitizes_html(member, comment_a):
    url = reverse("pontoon.edit_comment")

    # Make member the author
    comment_a.author = member.user
    comment_a.save()

    payload = "<img src=x onerror=alert(1)>safe"

    response = member.client.post(
        url,
        {"comment_id": comment_a.pk, "content": payload},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    assert response.status_code == 200

    comment_a.refresh_from_db()

    # Dangerous part should be removed
    assert "onerror" not in comment_a.content
    assert "<img" not in comment_a.content

    # Safe content should remain
    assert "safe" in comment_a.content


@pytest.mark.django_db
def test_delete_comment(member, client, comment_a):
    url = reverse("pontoon.delete_comment")

    # a user cannot delete someone elses comment
    response = member.client.post(
        url,
        {"comment_id": comment_a.pk, "content": "deleted"},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    assert response.status_code == 403

    # A user with can_manage_project permission can delete someone else's comment
    permission = Permission.objects.get(codename="can_manage_project")
    member.user.user_permissions.add(permission)
    member.user.refresh_from_db()

    response = member.client.post(
        url,
        {"comment_id": comment_a.pk},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )

    assert response.status_code == 200
    assert not Comment.objects.filter(pk=comment_a.pk).exists()

    # the author can delete their comment
    member.user.user_permissions.remove(permission)
    member.user.refresh_from_db()

    own_comment = TranslationCommentFactory(author=member.user)

    response = member.client.post(
        url,
        {"comment_id": own_comment.pk},
        HTTP_X_REQUESTED_WITH="XMLHttpRequest",
    )
    assert response.status_code == 200
    assert not Comment.objects.filter(pk=own_comment.pk).exists()
