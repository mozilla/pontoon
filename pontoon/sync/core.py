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
    TranslatedResource
)
from pontoon.sync.changeset import ChangeSet
from pontoon.sync.vcs.models import VCSProject
from pontoon.sync.utils import locale_directory_path

log = logging.getLogger(__name__)


def sync_project(db_project, now):
    # Only load source resources for updating entities.
    vcs_project = VCSProject(db_project, locales=[])
    with transaction.atomic():
        removed_paths = update_resources(db_project, vcs_project)
        changeset = ChangeSet(db_project, vcs_project, now)
        update_entities(db_project, vcs_project, changeset)
        changeset.execute()

    return changeset.changes['obsolete_db'], removed_paths


def serial_task(timeout, lock_key="", **celery_args):
    """
    Decorator ensures that there's only one running task with given task_name.
    Decorated tasks are bound tasks, meaning their first argument is always their Task instance
    :param timeout: time after which lock is released.
    :param lock_key: allows to define different lock for respective parameters of task.
    :param celery_args: argument passed to celery's shared_task decorator.
    """
    def wrapper(func):
        @shared_task(bind=True, **celery_args)
        @wraps(func)
        def wrapped_func(self, *args, **kwargs):
            lock_name = "serial_task.{}[{}]".format(self.name, lock_key.format(*args, **kwargs))
            # Acquire the lock
            if not cache.add(lock_name, True, timeout=timeout):
                raise RuntimeError("Can't execute task '{}' because the previously called"
                    " task is still running.".format(lock_name))
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
                raise ValueError(u'No entities found for key `{0}`'.format(key))
            else:
                # VCS no longer has the entity, obsolete it.
                changeset.obsolete_db_entity(db_entity)
        elif db_entity is None:
            # New VCS entities are added to Pontoon.
            changeset.create_db_entity(vcs_entity)


def update_resources(db_project, vcs_project):
    """Update the database on what resource files exist in VCS."""
    log.debug('Scanning {}'.format(vcs_project.source_directory_path()))
    relative_paths = vcs_project.resources.keys()
    removed_resources = db_project.resources.exclude(path__in=relative_paths)
    removed_paths = removed_resources.values_list('path', flat=True)
    log.debug('Removed paths: {}'.format(', '.join(removed_paths)))
    removed_resources.delete()

    for relative_path, vcs_resource in vcs_project.resources.items():
        resource, created = db_project.resources.get_or_create(path=relative_path)
        resource.format = Resource.get_path_format(relative_path)
        resource.total_strings = len(vcs_resource.entities)
        resource.save()
    return removed_paths


def update_translations(db_project, vcs_project, locale, changeset):
    for key, db_entity, vcs_entity in collect_entities(db_project, vcs_project):
        # If we don't have both the db_entity and vcs_entity we can't
        # do anything with the translations.
        if db_entity is None or vcs_entity is None:
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


def update_translated_resources(db_project, vcs_project, changeset, locale):
    """Update the TranslatedResource entries in the database."""
    for resource in db_project.resources.all():
        # We only want to create/update the TranslatedResource object if the
        # resource exists in the current locale, UNLESS the file is asymmetric.
        vcs_resource = vcs_project.resources.get(resource.path, None)
        if vcs_resource is not None:
            resource_exists = vcs_resource.files.get(locale) is not None
            if resource_exists or resource.is_asymmetric:
                translatedresource, _ = TranslatedResource.objects.get_or_create(resource=resource, locale=locale)
                translatedresource.calculate_stats()


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
