import factory

from pontoon.base.tests import ProjectFactory, RepositoryFactory
from pontoon.sync.models import ProjectSyncLog, RepositorySyncLog, SyncLog


class SyncLogFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = SyncLog


class ProjectSyncLogFactory(factory.django.DjangoModelFactory):
    sync_log = factory.SubFactory(SyncLogFactory)
    project = factory.SubFactory(ProjectFactory)

    class Meta:
        model = ProjectSyncLog


class RepositorySyncLogFactory(factory.django.DjangoModelFactory):
    project_sync_log = factory.SubFactory(ProjectSyncLogFactory)
    repository = factory.SubFactory(RepositoryFactory)

    class Meta:
        model = RepositorySyncLog
