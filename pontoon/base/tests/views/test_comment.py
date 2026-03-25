import pytest

from django.contrib.auth.models import Permission
from django.urls import reverse

from pontoon.base.models import Comment


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
def test_edit_comment(member, client, comment_a):
    url = reverse("pontoon.edit_comment")

    # a user cannot edit someone else's comment
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
