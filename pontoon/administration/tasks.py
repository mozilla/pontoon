import logging

from celery import shared_task

from django.core.management import call_command

from pontoon.base.tasks import PontoonTask


log = logging.getLogger(__name__)


@shared_task(base=PontoonTask, name="calculate_stats")
def calculate_stats_task():
    try:
        call_command("calculate_stats")
    except Exception as err:
        log.error(f"Calculate Stats failed: {err}")
