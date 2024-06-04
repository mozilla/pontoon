from django_jinja import library

from pontoon.sync.models import ProjectSyncLog


PROJECT_SYNC_LOG_STATUS = {
    ProjectSyncLog.IN_PROGRESS: "In-progress",
    ProjectSyncLog.SKIPPED: "Skipped",
    ProjectSyncLog.SYNCED: "Synced",
}


@library.global_function
def project_log_status_string(status):
    return PROJECT_SYNC_LOG_STATUS.get(status, "---")
