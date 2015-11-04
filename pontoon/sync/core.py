import logging
from collections import Counter

from django.contrib.auth.models import User
from django.db import connection, transaction
from django.template.loader import render_to_string
from django.utils import timezone


from pontoon.administration.vcs import CommitToRepositoryException
from pontoon.base.models import (
    ChangedEntityLocale,
    Entity,
    Resource,
    update_stats
)
from pontoon.sync.changeset import ChangeSet
from pontoon.sync.vcs_models import VCSProject


log = logging.getLogger(__name__)


@transaction.atomic
def sync_project(db_project, no_pull=False, no_commit=False):
    """
    Update the database with the current state of resources in version
    control and write any submitted translations from the database back
    to version control.
    """
    # Mark "now" at the start of sync to avoid messing with
    # translations submitted during sync.
    now = timezone.now()

    # Pull changes from VCS and update what we know about the files.
    if not no_pull:
        repos_changed = pull_changes(db_project)
    else:
        repos_changed = True  # Assume changed.

    # If the repos haven't changed since the last sync and there are
    # no Pontoon-side changes for this project, quit early.
    if not repos_changed and not db_project.needs_sync:
        log.info('Skipping project {0}, no changes detected.'.format(db_project.slug))
        return

    vcs_project = VCSProject(db_project)
    update_resources(db_project, vcs_project)

    # Collect all entities across VCS and the database and get their
    # keys so we can match up matching entities.
    vcs_entities = get_vcs_entities(vcs_project)
    db_entities = get_db_entities(db_project)
    entity_keys = set().union(db_entities.keys(), vcs_entities.keys())

    changeset = ChangeSet(db_project, vcs_project, now)
    for key in entity_keys:
        db_entity = db_entities.get(key, None)
        vcs_entity = vcs_entities.get(key, None)
        handle_entity(changeset, db_project, key, db_entity, vcs_entity)

    # Apply the changeset to the files, commit them, and update stats
    # entries in the DB.
    changeset.execute()
    if not no_commit:
        commit_changes(db_project, vcs_project, changeset)
    update_project_stats(db_project, vcs_project, changeset)

    # Clear out the "has_changed" markers now that we've finished
    # syncing.
    (ChangedEntityLocale.objects
        .filter(entity__resource__project=db_project, when__lte=now)
        .delete())
    db_project.has_changed = False
    db_project.save()

    # Clean up any duplicate approvals at the end of sync right
    # before we commit the transaction to avoid race conditions.
    with connection.cursor() as cursor:
        cursor.execute("""
            UPDATE base_translation AS b
            SET approved = FALSE, approved_date = NULL
            WHERE approved_date !=
                (SELECT max(approved_date)
                 FROM base_translation
                 WHERE entity_id = b.entity_id
                   AND locale_id = b.locale_id
                   AND (plural_form = b.plural_form OR plural_form IS NULL));
        """)

    log.info(u'Synced project {0}'.format(db_project.slug))


def handle_entity(changeset, db_project, key, db_entity, vcs_entity):
    """
    Determine what needs to be synced between the database and VCS versions
    of a single entity and log what needs to be changed in the changeset.
    """
    if vcs_entity is None:
        if db_entity is None:
            # This should never happen. What? Hard abort.
            raise ValueError('No entities found for key {0}'.format(key))
        else:
            # VCS no longer has the entity, remove it from Pontoon.
            changeset.obsolete_db_entity(db_entity)
    elif db_entity is None:
        # New VCS entities are added to Pontoon.
        changeset.create_db_entity(vcs_entity)
    else:
        for locale in db_project.locales.all():
            if not vcs_entity.has_translation_for(locale.code):
                # VCS lacks an entity for this locale, so we can't
                # pull updates nor edit it. Skip it!
                continue

            if db_entity.has_changed(locale):
                # Pontoon changes overwrite whatever VCS has.
                changeset.update_vcs_entity(locale.code, db_entity, vcs_entity)

            else:
                # If Pontoon has nothing or has not changed, and the VCS
                # still has the entity, update Pontoon with whatever may
                # have changed.
                changeset.update_db_entity(locale.code, db_entity, vcs_entity)


def update_resources(db_project, vcs_project):
    """Update the database on what resource files exist in VCS."""
    relative_paths = vcs_project.resources.keys()
    db_project.resources.exclude(path__in=relative_paths).delete()

    for relative_path, vcs_resource in vcs_project.resources.items():
        resource, created = db_project.resources.get_or_create(path=relative_path)
        resource.format = Resource.get_path_format(relative_path)
        resource.entity_count = len(vcs_resource.entities)
        resource.save()


def update_project_stats(db_project, vcs_project, changeset):
    """Update the Stats entries in the database."""
    for resource in db_project.resources.all():
        for locale in db_project.locales.all():
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


def commit_changes(db_project, vcs_project, changeset):
    """Commit the changes we've made back to the VCS."""
    for locale in db_project.locales.all():
        authors = changeset.commit_authors_per_locale.get(locale.code, [])

        # Use the top translator for this batch as commit author, or
        # the fake Pontoon user if there are no authors.
        if len(authors) > 0:
            commit_author = Counter(authors).most_common(1)[0][0]
        else:
            commit_author = User(first_name="Pontoon", email="pontoon@mozilla.com")

        commit_message = render_to_string('commit_message.jinja', {
            'locale': locale,
            'project': db_project,
            'authors': set(authors)
        })

        locale_path = vcs_project.locale_directory_path(locale.code)
        try:
            repo = db_project.repository_for_path(locale_path)
            result = repo.commit(commit_message, commit_author, locale_path)
        except (CommitToRepositoryException, ValueError) as err:
            result = {'message': unicode(err)}

        if result is not None:
            msg = (u'Committing project {project.name} for {locale.name} '
                   u'({locale.code}) failed: {reason}')
            log.info(msg.format(
                project=db_project,
                locale=locale,
                reason=result['message']
            ))
