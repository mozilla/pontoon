from django.contrib import messages
from django.shortcuts import get_object_or_404, redirect

from pontoon.admin.decorators import superuser_required
from pontoon.base.models import Project
from pontoon.sync.tasks import sync_project


@superuser_required
def project_trigger_sync(request, pk):
    """
    Queue a sync job for the project and redirect to it's change page.
    """
    project = get_object_or_404(Project, pk=pk)
    sync_project.delay(project.pk)
    messages.success(
        request,
        'Project {project.slug} has been queued for syncing.'.format(project=project)
    )
    return redirect('admin:base_project_change', project.pk)
