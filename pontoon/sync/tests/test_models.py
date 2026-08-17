from datetime import timedelta

import factory
import pytest

from django.test import override_settings
from django.utils import timezone

from pontoon.sync.models import Sync
from pontoon.sync.tasks import sync_project_task
from pontoon.test.factories import ProjectFactory


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


@pytest.mark.django_db
def test_sync_prev_busy():
    """A sync should abort if another sync for the same project is running."""
    project = ProjectFactory.create()
    SyncFactory.create(project=project, status=Sync.Status.IN_PROGRESS)

    with pytest.raises(RuntimeError):
        sync_project_task(project.pk, pull=False, commit=False, force=False)

    latest_sync = Sync.objects.filter(project=project).latest("pk")
    assert latest_sync.status == Sync.Status.PREV_BUSY


@pytest.mark.django_db
def test_sync_stale_lock_is_marked_incomplete():
    """
    An IN_PROGRESS sync older than SYNC_TASK_TIMEOUT is marked INCOMPLETE
    and does not block a new sync.
    """
    project = ProjectFactory.create()
    stale_sync = SyncFactory.create(project=project, status=Sync.Status.IN_PROGRESS)
    stale_sync.start_time = timezone.now() - timedelta(hours=2)
    stale_sync.save(update_fields=["start_time"])

    with override_settings(SYNC_TASK_TIMEOUT=60 * 60):
        sync_project_task(project.pk, pull=False, commit=False, force=False)

    stale_sync.refresh_from_db()
    assert stale_sync.status == Sync.Status.INCOMPLETE

    latest_sync = Sync.objects.filter(project=project).latest("pk")
    assert latest_sync.status == Sync.Status.FAIL
