from functools import wraps
import logging

from collections import Counter

from celery import shared_task
from django.contrib.auth.models import User

from django.core.cache import cache
from django.db import transaction
from django.template.loader import render_to_string

from pontoon.base.models import (
    Entity,
    Resource,
    update_stats
)
from pontoon.sync.changeset import ChangeSet
from pontoon.sync.vcs_models import VCSProject
from pontoon.sync.utils import locale_directory_path

log = logging.getLogger(__name__)


def sync_project(db_project, now):
    # Only load source resources for updating entities.
    vcs_project = VCSProject(db_project, locales=[])
    with transaction.atomic():
        update_resources(db_project, vcs_project)
        changeset = ChangeSet(db_project, vcs_project, now)
        update_entities(db_project, vcs_project, changeset)
        changeset.execute()


def serial_task(timeout, **celery_args):
    """
    Decorator ensures that there's only one running task with given task_name.
    Decorated tasks are bound tasks, meaning their first argument is always their Task instance
    :param timeout: time after which lock is released.
    """
    def wrapper(func):
        @shared_task(bind=True, **celery_args)
        @wraps(func)
        def wrapped_func(self, *args, **kwargs):
            lock_name = "serial_task.{}".format(self.name)
            # Acquire the lock
            if not cache.add(lock_name, True, timeout=timeout):
                raise RuntimeError("Can't execute task '{}' because the previously called"
                    " task is still running.".format(self.name))
            try:
                return func(self, *args, **kwargs)
            finally:
                # release the lock
                cache.delete(lock_name)
        return wrapped_func
    return wrapper


def collect_entities(db_project, vcs_project):
    """
    Find all the entities in the database and on the filesystem and
    match them together, yielding tuples of the form
    (entity_key, database_entity, vcs_entity).

    When a match isn't found, the missing entity will be None.
    """
    vcs_entities = get_vcs_entities(vcs_project)
    db_entities = get_db_entities(db_project)
    entity_keys = set().union(db_entities.keys(), vcs_entities.keys())

    for key in entity_keys:
        yield key, db_entities.get(key, None), vcs_entities.get(key, None)


def update_entities(db_project, vcs_project, changeset):
    for key, db_entity, vcs_entity in collect_entities(db_project, vcs_project):
        if vcs_entity is None:
            if db_entity is None:
                # This should never happen. What? Hard abort.
                raise ValueError('No entities found for key {0}'.format(key))
            else:
                # VCS no longer has the entity, obsolete it.
                changeset.obsolete_db_entity(db_entity)
        elif db_entity is None:
            # New VCS entities are added to Pontoon.
            changeset.create_db_entity(vcs_entity)


def update_resources(db_project, vcs_project):
    """Update the database on what resource files exist in VCS."""
    relative_paths = vcs_project.resources.keys()
    db_project.resources.exclude(path__in=relative_paths).delete()

    for relative_path, vcs_resource in vcs_project.resources.items():
        resource, created = db_project.resources.get_or_create(path=relative_path)
        resource.format = Resource.get_path_format(relative_path)
        resource.entity_count = len(vcs_resource.entities)
        resource.save()


def update_translations(db_project, vcs_project, locale, changeset):
    for key, db_entity, vcs_entity in collect_entities(db_project, vcs_project):
        # We shouldn't hit this situation in a real sync, but we might
        # hit it during a test, so log it and continue just in case.
        if db_entity is None or vcs_entity is None:
            log.warning('Could not find VCS/DB entity for key {key} while '
                        'updating translations, skipping.'.format(key=key))
            continue

        if not vcs_entity.has_translation_for(locale.code):
            # VCS lacks an entity for this locale, so we can't
            # pull updates nor edit it. Skip it!
            continue
        if db_entity.has_changed(locale):
            # Pontoon changes overwrite whatever VCS has.
            changeset.update_vcs_entity(locale, db_entity, vcs_entity)
        else:
            # If Pontoon has nothing or has not changed, and the VCS
            # still has the entity, update Pontoon with whatever may
            # have changed.
            changeset.update_db_entity(locale, db_entity, vcs_entity)


def update_project_stats(db_project, vcs_project, changeset, locale):
    """Update the Stats entries in the database."""
    for resource in db_project.resources.all():
        # We only want to create/update the stats object if the resource
        # exists in the current locale, UNLESS the file is asymmetric.
        vcs_resource = vcs_project.resources[resource.path]
        resource_exists = vcs_resource.files.get(locale) is not None
        if resource_exists or resource.is_asymmetric:
            update_stats(resource, locale)


def get_vcs_entities(vcs_project):
    return {entity_key(entity): entity for entity in vcs_project.entities}


def get_db_entities(db_project):
    entities = (Entity.objects
                .select_related('resource')
                .prefetch_related('changed_locales')
                .filter(resource__project=db_project, obsolete=False))
    return {entity_key(entity): entity for entity in entities}


def entity_key(entity):
    """
    Generate a key for the given entity that is unique within the
    project.
    """
    key = entity.key or entity.string
    return ':'.join([entity.resource.path, key])


def pull_changes(db_project):
    """
    Update the local files with changes from the VCS. Returns
    whether any of the updated repos have changed since the last
    sync, based on the revision numbers.
    """
    changed = False
    for repo in db_project.repositories.all():
        repo_revisions = repo.pull()

        # If any revision is None, we can't be sure if a change
        # happened or not, so we default to assuming it did.
        unsure_change = None in repo_revisions.values()
        if unsure_change or repo_revisions != repo.last_synced_revisions:
            changed = True

        repo.last_synced_revisions = repo_revisions
        repo.save()

    return changed


def commit_changes(db_project, vcs_project, changeset, locale):
    """Commit the changes we've made back to the VCS."""
    authors = changeset.commit_authors_per_locale.get(locale.code, [])

    # Use the top translator for this batch as commit author, or
    # the fake Pontoon user if there are no authors.
    if len(authors) > 0:
        commit_author = Counter(authors).most_common(1)[0][0]
    else:
        commit_author = User(first_name="Mozilla Pontoon", email="pontoon@mozilla.com")

    commit_message = render_to_string('sync/commit_message.jinja', {
        'locale': locale,
        'project': db_project,
        'authors': set(authors)
    })

    locale_path = locale_directory_path(vcs_project.checkout_path, locale.code)
    repo = db_project.repository_for_path(locale_path)
    repo.commit(commit_message, commit_author, locale_path)
