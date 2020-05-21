import pytest
from django.contrib.auth.models import User

from pontoon.base.tests import ProjectFactory


@pytest.mark.django_db
def test_filter_users_by_project_visibility(admin, user_a):
    all_users_pks = [admin.pk, user_a.pk]
    superuser_pks = [admin.pk]
    all_users = User.objects.filter(pk__in=all_users_pks)
    superusers = User.objects.filter(pk__in=superuser_pks)

    public_project = ProjectFactory.create(visibility="public")
    private_project = ProjectFactory.create()

    assert list(
        User.projects.filter_visibility(public_project).filter(pk__in=all_users_pks,)
    ) == list(all_users)
    assert list(
        User.projects.filter_visibility(private_project).filter(pk__in=all_users_pks,)
    ) == list(superusers)
