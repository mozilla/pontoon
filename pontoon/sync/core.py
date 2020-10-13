from functools import wraps
import logging
import requests

from celery import shared_task
from collections import Counter

from django.conf import settings
from django.contrib.auth.models import User
from django.core.cache import cache
from django.db import transaction
from django.template.loader import render_to_string

from pontoon.base.models import (
    Entity,
    Locale,
    Resource,
    TranslatedResource,
)
from pontoon.sync.changeset import ChangeSet
from pontoon.sync.vcs.models import VCSProject


log = logging.getLogger(__name__)


def update_originals(db_project, now, force=False):
    vcs_project = VCSProject(db_project, locales=[], force=force)

    with transaction.atomic():
        added_paths, removed_paths, changed_paths = update_resources(
            db_project, vcs_project
        )
        changeset = ChangeSet(db_project, vcs_project, now)
        update_entities(db_project, vcs_project, changeset)
        changeset.execute()

    return added_paths, removed_paths, changed_paths, changeset.new_entities


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
            lock_name = "serial_task.{}[{}]".format(
                self.name, lock_key.format(*args, **kwargs)
            )
            # Acquire the lock
            if not cache.add(lock_name, True, timeout=timeout):
                error = RuntimeError(
                    "Can't execute task '{}' because the previously called "
                    "task is still running.".format(lock_name)
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


def collect_entities(db_project, vcs_project, changed_resources):
    """
    Find all the entities in the database and on the filesystem and
    match them together, yielding tuples of the form
    (entity_key, database_entity, vcs_entity).

    When a match isn't found, the missing entity will be None.
    """
    db_entities = get_db_entities(db_project, changed_resources)
    vcs_entities = get_vcs_entities(vcs_project)
    entity_keys = set().union(db_entities.keys(), vcs_entities.keys())

    for key in entity_keys:
        yield key, db_entities.get(key, None), vcs_entities.get(key, None)


def update_entities(db_project, vcs_project, changeset):
    changed_resources = vcs_project.changed_files
    for key, db_entity, vcs_entity in collect_entities(
        db_project, vcs_project, changed_resources
    ):
        if vcs_entity is None:
            if db_entity is None:
                # This should never happen. What? Hard abort.
                raise ValueError(u"No entities found for key `{0}`".format(key))
            else:
                # VCS no longer has the entity, obsolete it.
                changeset.obsolete_db_entity(db_entity)
        elif db_entity is None:
            # New VCS entities are added to Pontoon.
            changeset.create_db_entity(vcs_entity)
        else:
            changeset.update_db_source_entity(db_entity, vcs_entity)


def update_resources(db_project, vcs_project):
    """Update the database on what resource files exist in VCS."""
    log.debug("Scanning {}".format(vcs_project.source_directory_path))
    vcs_changed_files, vcs_removed_files = vcs_project.changed_source_files

    removed_resources = db_project.resources.filter(path__in=vcs_removed_files)
    removed_paths = removed_resources.values_list("path", flat=True)

    changed_resources = db_project.resources.filter(path__in=vcs_changed_files)
    changed_paths = changed_resources.values_list("path", flat=True)

    added_paths = []

    log.debug("Removed files: {}".format(", ".join(removed_paths) or "None"))
    removed_resources.delete()

    for relative_path, vcs_resource in vcs_project.resources.items():
        resource, created = db_project.resources.get_or_create(path=relative_path)
        resource.format = Resource.get_path_format(relative_path)
        resource.total_strings = len(vcs_resource.entities)
        resource.save()

        if created:
            added_paths.append(relative_path)

    log.debug("Added files: {}".format(", ".join(added_paths) or "None"))
    return added_paths, removed_paths, changed_paths


def get_changed_resources(db_project, vcs_project):
    changed_resources = vcs_project.changed_files

    if db_project.unsynced_locales:
        changed_resources = None

    if changed_resources is not None:
        changed_resources = (
            list(changed_resources.keys())
            + list(vcs_project.added_paths)
            + list(vcs_project.changed_paths)
        )

    return changed_resources


def update_translations(db_project, vcs_project, locale, changeset):
    changed_resources = get_changed_resources(db_project, vcs_project)
    all_entities = collect_entities(db_project, vcs_project, changed_resources)
    for key, db_entity, vcs_entity in all_entities:
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


def update_translated_resources(db_project, vcs_project, locale):
    """
    Update the TranslatedResource entries in the database.
    Returns true if a new TranslatedResource is added to the locale.
    """
    if vcs_project.configuration:
        return update_translated_resources_with_config(db_project, vcs_project, locale,)
    else:
        return update_translated_resources_without_config(
            db_project, vcs_project, locale,
        )


def update_translated_resources_with_config(db_project, vcs_project, locale):
    """
    Create/update the TranslatedResource objects for each Resource instance
    that is enabled for the given locale through project configuration.
    """
    tr_created = False

    for resource in vcs_project.configuration.locale_resources(locale):
        translatedresource, created = TranslatedResource.objects.get_or_create(
            resource=resource, locale=locale
        )

        if created:
            tr_created = True
        translatedresource.calculate_stats()

    return tr_created


def update_translated_resources_without_config(db_project, vcs_project, locale):
    """
    We only want to create/update the TranslatedResource object if the
    resource exists in the current locale, UNLESS the file is asymmetric.
    """
    tr_created = False

    for resource in db_project.resources.all():
        vcs_resource = vcs_project.resources.get(resource.path, None)

        if vcs_resource is not None:
            resource_exists = vcs_resource.files.get(locale) is not None
            if resource_exists or resource.is_asymmetric:
                translatedresource, created = TranslatedResource.objects.get_or_create(
                    resource=resource, locale=locale
                )

                if created:
                    tr_created = True
                translatedresource.calculate_stats()

    return tr_created


def update_translated_resources_no_files(db_project, locale, changed_resources):
    """
    Create/update TranslatedResource entries if files aren't available. This typically happens when
    originals change and translations don't, so we don't pull locale repositories.
    """
    for resource in changed_resources:
        # We can only update asymmetric (monolingual) TranslatedResources. For bilingual files we
        # only create TranslatedResources if the file is present in the repository for the locale,
        # which we cannot check without files.
        if not resource.is_asymmetric:
            log.error(
                "Unable to calculate stats for asymmetric resource: {resource}.".format(
                    resource
                )
            )
            continue

        translatedresource, _ = TranslatedResource.objects.get_or_create(
            resource=resource, locale=locale
        )
        translatedresource.calculate_stats()


def get_vcs_entities(vcs_project):
    return {entity_key(entity): entity for entity in vcs_project.entities}


def get_changed_entities(db_project, changed_resources):
    entities = (
        Entity.objects.select_related("resource")
        .prefetch_related("changed_locales")
        .filter(resource__project=db_project, obsolete=False)
    )

    if changed_resources is not None:
        entities = entities.filter(resource__path__in=changed_resources)
    return entities


def get_db_entities(db_project, changed_resources=None):
    return {
        entity_key(entity): entity
        for entity in get_changed_entities(db_project, changed_resources)
    }


def entity_key(entity):
    """
    Generate a key for the given entity that is unique within the
    project.
    """
    key = entity.key or entity.string
    return ":".join([entity.resource.path, key])


def has_repo_changed(last_synced_revisions, pulled_revisions):
    has_changed = False

    # If any revision is None, we can't be sure if a change
    # happened or not, so we default to assuming it did.
    unsure_change = None in pulled_revisions.values()

    if unsure_change or pulled_revisions != last_synced_revisions:
        has_changed = True

    return has_changed


def pull_source_repo_changes(db_project):
    source_repo = db_project.source_repository
    pulled_revisions = source_repo.pull()
    has_changed = has_repo_changed(source_repo.last_synced_revisions, pulled_revisions)
    return has_changed


def pull_locale_repo_changes(db_project, locales):
    """
    Update the local files with changes from the VCS. Returns True
    if any of the updated repos have changed since the last sync.
    """
    has_changed = False
    repo_locales = {}

    # If none of the locales have changed, quit early.
    if not locales:
        return has_changed, repo_locales

    # Skip already pulled locales. Useful for projects with multiple repositories,
    # since we don't store the information what locale belongs to what repository.
    pulled_locales = []

    for repo in db_project.translation_repositories():
        remaining_locales = locales.exclude(code__in=pulled_locales)
        if not remaining_locales:
            break

        pulled_revisions = repo.pull(remaining_locales)
        repo_locales[repo.pk] = Locale.objects.filter(code__in=pulled_revisions.keys())
        pulled_locales += pulled_revisions.keys()

        if has_repo_changed(repo.last_synced_revisions, pulled_revisions):
            has_changed = True

    return has_changed, repo_locales


def commit_changes(db_project, vcs_project, changeset, locale):
    """Commit the changes we've made back to the VCS."""
    authors = changeset.commit_authors_per_locale.get(locale.code, [])

    # Use the top translator for this batch as commit author, or
    # the fake Pontoon user if there are no authors.
    if len(authors) > 0:
        commit_author = Counter(authors).most_common(1)[0][0]
    else:
        commit_author = User(
            first_name=settings.VCS_SYNC_NAME, email=settings.VCS_SYNC_EMAIL
        )

    commit_message = render_to_string(
        "sync/commit_message.jinja",
        {"locale": locale, "project": db_project, "authors": set(authors)},
    )

    locale_path = vcs_project.locale_directory_paths[locale.code]
    repo = db_project.repository_for_path(locale_path)
    repo.commit(commit_message, commit_author, locale_path)


def get_changed_locales(db_project, locales, now):
    """
    Narrow down locales to the ones that have changed since the last sync by fetching latest
    repository commit hashes via API. For projects with many repositories, this is much faster
    than running VCS pull/clone for each repository.
    """
    repos = db_project.translation_repositories()

    # Requirement: all translation repositories must have API configured.
    for repo in repos:
        if not repo.api_config:
            return locales

    log.info(
        "Fetching latest commit hashes for project {0} started.".format(db_project.slug)
    )

    # If locale has changed in the DB, we need to sync it.
    changed_locale_pks = list(
        locales.filter(
            changedentitylocale__entity__resource__project=db_project,
            changedentitylocale__when__lte=now,
        ).values_list("pk", flat=True)
    )

    unchanged_locale_pks = []
    error_locale_pks = set()

    for repo in repos:
        for locale in locales:
            # If we already processed the locale, we can move on.
            if locale.pk in changed_locale_pks + unchanged_locale_pks:
                continue

            try:
                locale_api_endpoint = repo.api_config["endpoint"].format(
                    locale_code=locale.code
                )
                response = requests.get(locale_api_endpoint)

                # Raise exception on 4XX client error or 5XX server error response
                response.raise_for_status()

                # If locale has not synced yet, we need to sync it.
                last_synced_commit_id = repo.get_last_synced_revisions(locale.code)
                if not last_synced_commit_id:
                    changed_locale_pks.append(locale.pk)
                    continue

                # If locale has changed in the VCS, we need to sync it.
                latest_commit_id = repo.api_config["get_key"](response.json())
                if not latest_commit_id.startswith(last_synced_commit_id):
                    changed_locale_pks.append(locale.pk)

                # If locale hasn't changed in the VCS, we don't need to sync it.
                else:
                    unchanged_locale_pks.append(locale.pk)

            # Errors and exceptions can mean locale is in a different repository or indicate
            # an actual network problem.
            except requests.exceptions.RequestException:
                error_locale_pks.add(locale.pk)

    # Check if any locale for which the exception was raised hasn't been processed yet.
    # For those locales we can't be sure if a change happened, so we assume it did.
    for l in error_locale_pks:
        if l not in changed_locale_pks + unchanged_locale_pks:
            log.error(
                "Unable to fetch latest commit hash for locale {locale} in project {project}".format(
                    locale=Locale.objects.get(pk=l), project=db_project.slug
                )
            )
            changed_locale_pks.append(locale.pk)

    changed_locales = db_project.locales.filter(pk__in=changed_locale_pks)

    log.info(
        "Fetching latest commit hashes for project {project} complete. Changed locales: {locales}.".format(
            project=db_project.slug,
            locales=", ".join(changed_locales.values_list("code", flat=True)),
        )
    )

    return changed_locales
