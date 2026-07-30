import io

from unittest.mock import patch

import pytest

from django.core.management.base import CommandError

from pontoon.base.models import Project
from pontoon.sync.management.commands import sync_projects
from pontoon.test.factories import ProjectFactory


@pytest.fixture
def command():
    command = sync_projects.Command()
    command.verbosity = 0
    command.commit = True
    command.pull = True
    command.force = False
    command.stderr = io.StringIO()
    return command


@pytest.fixture
def mock_sync_project_task():
    with patch.object(sync_projects, "sync_project_task") as mock:
        yield mock


def execute_command(command, *args, **kwargs):
    kwargs.setdefault("verbosity", 0)
    kwargs.setdefault("no_commit", False)
    kwargs.setdefault("no_pull", False)
    kwargs.setdefault("force", False)

    command.handle(*args, **kwargs)


@pytest.mark.django_db
def test_syncable_projects_only(command, mock_sync_project_task):
    """
    Only sync projects that aren't disabled
    and for which sync isn't disabled.
    """
    ProjectFactory.create(disabled=True)
    ProjectFactory.create(sync_disabled=True)
    active_project = ProjectFactory.create(
        disabled=False,
        sync_disabled=False,
    )

    execute_command(command)
    mock_sync_project_task.delay.assert_called_with(
        active_project.pk, pull=True, commit=True, force=False
    )


@pytest.mark.django_db
def test_non_repository_projects(command, mock_sync_project_task):
    """Only sync projects with data_source=repository."""
    ProjectFactory.create(data_source=Project.DataSource.DATABASE)
    repo_project = ProjectFactory.create(data_source=Project.DataSource.REPOSITORY)

    execute_command(command)
    mock_sync_project_task.delay.assert_called_with(
        repo_project.pk, pull=True, commit=True, force=False
    )


@pytest.mark.django_db
def test_project_slugs(command, mock_sync_project_task):
    """
    If project slugs are passed to Command.handle, only sync projects
    matching those slugs.
    """
    ignore_project, handle_project = ProjectFactory.create_batch(2)

    execute_command(command, projects=handle_project.slug)
    mock_sync_project_task.delay.assert_called_with(
        handle_project.pk, pull=True, commit=True, force=False
    )


@pytest.mark.django_db
def test_no_matching_projects(command, mock_sync_project_task):
    """
    If no projects are found that match the given slugs, raise a
    CommandError.
    """
    with pytest.raises(CommandError):
        execute_command(command, projects="does-not-exist")


@pytest.mark.django_db
def test_invalid_slugs(command, mock_sync_project_task):
    """
    If some of projects have invalid slug, we should warn user about them.
    """
    handle_project = ProjectFactory.create()

    execute_command(command, projects=handle_project.slug + ",aaa,bbb")

    mock_sync_project_task.delay.assert_called_with(
        handle_project.pk, pull=True, commit=True, force=False
    )

    assert (
        command.stderr.getvalue()
        == "Couldn't find projects to sync with following slugs: aaa, bbb"
    )


@pytest.mark.django_db
def test_options(command, mock_sync_project_task):
    project = ProjectFactory.create()
    execute_command(command, no_pull=True, no_commit=True)
    mock_sync_project_task.delay.assert_called_with(
        project.pk, pull=False, commit=False, force=False
    )
