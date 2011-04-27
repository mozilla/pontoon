#!/usr/bin/env python
import logging
import os
import site
import sys


current_settings = None
execute_manager = None
log = logging.getLogger(__name__)
ROOT = None


def path(*a):
    return os.path.join(ROOT, *a)


def setup_environ(manage_file, settings=None):
    """Sets up a Django app within a manage.py file.

    Keyword Arguments

    **settings**
        An imported settings module. Without this, playdoh tries to import
        these modules (in order): settings_local, settings

    """
    # sys is global to avoid undefined local
    global sys, current_settings, execute_manager, ROOT

    ROOT = os.path.dirname(os.path.abspath(manage_file))

    # Adjust the python path and put local packages in front.
    prev_sys_path = list(sys.path)

    # Make settings_local importable
    sys.path.append(os.getcwd())

    site.addsitedir(path('apps'))
    site.addsitedir(path('lib'))

    # Local (project) vendor library
    site.addsitedir(path('vendor-local'))
    site.addsitedir(path('vendor-local/lib/python'))

    # Global (upstream) vendor library
    site.addsitedir(path('vendor'))
    site.addsitedir(path('vendor/lib/python'))

    # Move the new items to the front of sys.path. (via virtualenv)
    new_sys_path = []
    for item in list(sys.path):
        if item not in prev_sys_path:
            new_sys_path.append(item)
            sys.path.remove(item)
    sys.path[:0] = new_sys_path

    from django.core.management import execute_manager, setup_environ

    if not settings:
        try:
            import settings_local as settings
        except ImportError:
            try:
                import settings
            except ImportError:
                import sys
                sys.stderr.write(
                    "Error: Tried importing 'settings_local.py' and "
                    "'settings.py' but neither could be found (or they're "
                    "throwing an ImportError)."
                    " Please come back and try again later.")
                raise
    current_settings = settings

    # If we want to use django settings anywhere, we need to set up the
    # required environment variables.
    setup_environ(settings)

    # Monkey-patch django forms to avoid having to use Jinja2's |safe
    # everywhere.
    import safe_django_forms
    safe_django_forms.monkeypatch()

    # Configure Celery (optional)
    try:
        import djcelery
    except ImportError, exc:
        log.warning('%s (playdoh did not initialize djcelery)' % exc)
    else:
        djcelery.setup_loader()


def main():
    execute_manager(current_settings)
