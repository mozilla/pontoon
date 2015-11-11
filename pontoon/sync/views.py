from django.shortcuts import get_object_or_404, render

from pontoon.sync.models import SyncLog


def sync_log_list(request):
    return render(request, 'sync/log_list.html', {
        'sync_logs': SyncLog.objects.order_by('-start_time'),
    })


def sync_log_details(request, sync_log_pk):
    # Prefetch for the end_time
    queryset = SyncLog.objects.prefetch_related(
        'project_sync_logs__repository_sync_logs__repository',
        'project_sync_logs__project__repositories',
    )

    sync_log = get_object_or_404(queryset, pk=sync_log_pk)
    project_sync_logs = sync_log.project_sync_logs.all()
    repository_sync_logs = {
        project_log: project_log.repository_sync_logs.all()
        for project_log in project_sync_logs
    }

    return render(request, 'sync/log_details.html', {
        'sync_log': sync_log,
        'project_sync_logs': project_sync_logs,
        'repository_sync_logs': repository_sync_logs,
    })
