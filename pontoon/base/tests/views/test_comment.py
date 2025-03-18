import pytest

from django.contrib.auth.models import Permission
from django.urls import reverse


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
