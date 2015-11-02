from celery import Task

from pontoon.base.errors import send_exception


class PontoonTask(Task):
    """Common functionality for all Pontoon celery tasks."""
    abstract = True

    def on_failure(self, exc, task_id, args, kwargs, einfo):
        send_exception(exc, exc_info=einfo)
