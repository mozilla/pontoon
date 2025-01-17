from datetime import datetime

from django_jinja import library

from pontoon.sync.models import Sync


@library.global_function
def format_sync_duration(start_time: datetime, end_time: datetime | None) -> str:
    if not end_time:
        return "…"
    td = end_time - start_time
    minutes = td.days * 24 * 60 + td.seconds // 60
    seconds = td.seconds % 60
    if minutes > 1:
        min_str = f"{minutes} minutes, "
    elif minutes == 1:
        min_str = "1 minute, "
    else:
        min_str = ""
    sec_str = "1 second" if seconds == 1 else f"{seconds} seconds"
    return min_str + sec_str


@library.global_function
def format_sync_status_class(status: Sync.Status | None) -> str:
    match status:
        case Sync.Status.FAIL | Sync.Status.INCOMPLETE:
            return "sync-status-fail"
        case Sync.Status.DONE:
            return "sync-status-success"
        case Sync.Status.NO_CHANGES | None:
            return "sync-status-other"
        case _:
            return "sync-status-warn"


@library.global_function
def format_sync_status_label(status: Sync.Status | None) -> str:
    try:
        return "–" if status is None else Sync.Status(status).label
    except Exception:
        return f"??? ({status})"
