import sys

from celery import Task

from pontoon.base.errors import send_exception


class PontoonTask(Task):
    """Common functionality for all Pontoon celery tasks."""

    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        # Celery throws away the traceback instance and creates its own,
        # but inspect can't process their custom class.
        _, _, traceback = sys.exc_info()
        send_exception(exc, exc_info=(einfo.type, exc, traceback))
