import pytest
from django.contrib.auth.models import User

from pontoon.base.tests import ProjectFactory
from pontoon.projects.utils import filter_users_by_project_visibility


@pytest.mark.django_db
def test_filter_users_by_project_visibility(admin, user_a):
    all_users = User.objects.filter(pk__in=[admin.pk, user_a.pk])
    superusers = User.objects.filter(pk__in=[admin.pk])

    public_project = ProjectFactory.create(visibility="public")
    private_project = ProjectFactory.create()

    assert list(filter_users_by_project_visibility(public_project, all_users)) == list(
        all_users
    )
    assert list(filter_users_by_project_visibility(private_project, all_users)) == list(
        superusers
    )
