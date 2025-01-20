import factory
import pytest

from django.utils import timezone

from pontoon.base.tests import ProjectFactory
from pontoon.sync.models import Sync
from pontoon.sync.tasks import sync_project_task


class SyncFactory(factory.django.DjangoModelFactory):
    project = factory.SubFactory(ProjectFactory)

    class Meta:
        model = Sync


@pytest.mark.django_db
def test_sync_done():
    test_start_time = timezone.now()
    sync: Sync = SyncFactory.create()
    assert sync.status == Sync.Status.IN_PROGRESS
    assert sync.start_time >= test_start_time
    assert sync.end_time is None

    sync.done(Sync.Status.NO_CHANGES)
    assert sync.status == Sync.Status.NO_CHANGES
    assert sync.end_time >= sync.start_time
    assert sync.error == ""


@pytest.mark.django_db
def test_sync_smoke():
    test_start_time = timezone.now()
    project = ProjectFactory.create()
    sync_project_task(project.pk, pull=False, commit=False, force=False)

    sync = Sync.objects.get(project=project)
    assert sync.start_time >= test_start_time
    assert sync.end_time >= sync.start_time
    # Not a directory: .../media/projects/project-0
    assert sync.status == Sync.Status.FAIL
    assert sync.error != ""
