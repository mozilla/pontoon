import logging
from functools import wraps

from celery import shared_task
from django.core.cache import cache

log = logging.getLogger(__name__)


def serial_task(timeout, lock_key="", on_error=None, **celery_args):
    """
    Decorator ensures that there's only one running task with given task_name.
    Decorated tasks are bound tasks, meaning their first argument is always their Task instance
    :param timeout: time after which lock is released.
    :param lock_key: allows to define different lock for respective parameters of task.
    :param on_error: callback to be executed if an error is raised.
    :param celery_args: argument passed to celery's shared_task decorator.
    """

    def wrapper(func):
        @shared_task(bind=True, **celery_args)
        @wraps(func)
        def wrapped_func(self, *args, **kwargs):
            lock_name = f"serial_task.{self.name}[{lock_key.format(*args, **kwargs)}]"
            # Acquire the lock
            if not cache.add(lock_name, True, timeout=timeout):
                error = RuntimeError(
                    f"Can't execute task '{lock_name}' because the previously called task is still running."
                )
                if callable(on_error):
                    on_error(error, *args, **kwargs)
                raise error
            try:
                return func(self, *args, **kwargs)
            finally:
                # release the lock
                cache.delete(lock_name)

        return wrapped_func

    return wrapper
