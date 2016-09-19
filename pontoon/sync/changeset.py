from collections import defaultdict
import logging
import os

from bulk_update.helper import bulk_update
from django.db.models import Prefetch

from pontoon.base.models import (
    Entity,
    Locale,
    Resource,
    Translation,
    TranslationMemoryEntry
)
from pontoon.base.utils import match_attr

log = logging.getLogger(__name__)

class ChangeSet(object):
    """
    Stores a set of changes to be made to the database and the
    translations stored in VCS. Once all the necessary changes have been
    stored, execute all the changes at once efficiently.
    """
    def __init__(self, db_project, vcs_project, now, obsolete_vcs_entities=None, obsolete_vcs_resources=None, locale=None):
        """
        :param now:
            Datetime to use for marking when approvals happened.
        """
        self.db_project = db_project
        self.vcs_project = vcs_project
        self.now = now
        self.locale = locale

        # Store locales and resources for FK relationships.
        self.locales = {l.code: l for l in Locale.objects.all()}
        self.resources = {r.path: r for r in self.db_project.resources.all()}

        self.executed = False
        self.changes = {
            'update_vcs': [],
            'obsolete_vcs_entities': obsolete_vcs_entities or [],
            'obsolete_vcs_resources': obsolete_vcs_resources or [],
            'update_db': [],
            'obsolete_db': [],
            'create_db': []
        }

        self.entities_to_update = []
        self.translations_to_update = []
        self.translations_to_create = []
        self.commit_authors_per_locale = defaultdict(list)
        self.locales_to_commit = set()

    def update_vcs_entity(self, locale, db_entity, vcs_entity):
        """
        Replace the translations in VCS with the translations from the
        database.
        Updates only entities that has been changed.
        """
        if db_entity.has_changed(locale):
            self.changes['update_vcs'].append((locale.code, db_entity, vcs_entity))
            self.locales_to_commit.add(locale)

    def create_db_entity(self, vcs_entity):
        """Create a new entity in the database."""
        self.changes['create_db'].append(vcs_entity)

    def update_db_entity(self, locale, db_entity, vcs_entity):
        """Update the database with translations from VCS."""
        self.changes['update_db'].append((locale.code, db_entity, vcs_entity))

    def update_db_source_entity(self, db_entity, vcs_entity):
        """Update the entities with the latest data from vcs."""
        self.changes['update_db'].append((None, db_entity, vcs_entity))

    def obsolete_db_entity(self, db_entity):
        """Mark the given entity as obsolete."""
        self.changes['obsolete_db'].append(db_entity.pk)

    def execute(self):
        """
        Execute the changes stored in this changeset. Execute can only
        be called once per changeset; subsequent calls raise a
        RuntimeError, even if the changes failed.
        """
        if self.executed:
            raise RuntimeError('execute() can only be called once per changeset.')
        else:
            self.executed = True

        # Perform the changes and fill the lists for bulk creation and
        # updating.
        self.execute_update_vcs()
        self.execute_create_db()
        self.execute_update_db()
        self.execute_obsolete_db()
        self.execute_obsolete_vcs_resources()

        # Apply the built-up changes to the DB
        self.bulk_update_entities()
        self.bulk_create_translations()
        self.bulk_update_translations()

    def execute_update_vcs(self):
        resources = self.vcs_project.resources
        changed_resources = set()

        for locale_code, db_entity, vcs_entity in self.changes['update_vcs']:
            changed_resources.add(resources[db_entity.resource.path])
            vcs_translation = vcs_entity.translations[locale_code]
            db_translations = (db_entity.translation_set
                .filter(approved=True, locale__code=locale_code)
            )
            vcs_translation.update_from_db(db_translations)

            # Track which translators were involved.
            self.commit_authors_per_locale[locale_code].extend([t.user for t in db_translations if t.user])

        # Remove obsolete entities from asymmetric files
        obsolete_entities_paths = Resource.objects.obsolete_entities_paths(
            self.changes['obsolete_vcs_entities']
        )

        for path in obsolete_entities_paths:
            changed_resources.add(resources[path])

        if len(obsolete_entities_paths) > 0:
            self.locales_to_commit = set(self.locales.values())

        for resource in changed_resources:
            resource.save(self.locale)

    def get_entity_updates(self, vcs_entity):
        """
        Return a dict of the properties and values necessary to create
        or update a database entity from a VCS entity.
        """
        return {
            'resource': self.resources[vcs_entity.resource.path],
            'string': vcs_entity.string,
            'string_plural': vcs_entity.string_plural,
            'key': vcs_entity.key,
            'comment': '\n'.join(vcs_entity.comments),
            'order': vcs_entity.order,
            'source': vcs_entity.source
        }

    def execute_create_db(self):
        for vcs_entity in self.changes['create_db']:
            entity = Entity(**self.get_entity_updates(vcs_entity))
            entity.save()  # We can't use bulk_create since we need a PK

            for locale_code, vcs_translation in vcs_entity.translations.items():
                for plural_form, string in vcs_translation.strings.items():
                    self.translations_to_create.append(Translation(
                        entity=entity,
                        locale=self.locales[locale_code],
                        string=string,
                        plural_form=plural_form,
                        approved=not vcs_translation.fuzzy,
                        approved_date=self.now if not vcs_translation.fuzzy else None,
                        fuzzy=vcs_translation.fuzzy
                    ))

    def update_entity_translations_from_vcs(
            self, db_entity, locale_code, vcs_translation,
            user=None, db_translations=None, old_translations=None
    ):
        if db_translations is None:
            db_translations = db_entity.translation_set.filter(
                locale__code=locale_code,
            )
        approved_translations = []
        fuzzy_translations = []

        for plural_form, string in vcs_translation.strings.items():
            # Check if we need to modify an existing translation or
            # create a new one.
            db_translation = match_attr(db_translations,
                                        plural_form=plural_form,
                                        string=string)
            if db_translation:
                if not db_translation.approved and not vcs_translation.fuzzy:
                    db_translation.approved = True
                    db_translation.approved_date = self.now
                    db_translation.approved_user = user
                db_translation.fuzzy = vcs_translation.fuzzy
                db_translation.extra = vcs_translation.extra

                if db_translation.is_dirty():
                    self.translations_to_update.append(db_translation)
                if not db_translation.fuzzy:
                    approved_translations.append(db_translation)
                else:
                    fuzzy_translations.append(db_translation)
            else:
                self.translations_to_create.append(Translation(
                    entity=db_entity,
                    locale=self.locales[locale_code],
                    string=string,
                    plural_form=plural_form,
                    approved=not vcs_translation.fuzzy,
                    approved_date=self.now if not vcs_translation.fuzzy else None,
                    approved_user=user,
                    user=user,
                    fuzzy=vcs_translation.fuzzy,
                    extra=vcs_translation.extra
                ))

        # Any existing translations that were not approved get unapproved.
        if old_translations is None:
            old_translations = db_translations.filter(approved_date__lte=self.now)

        for translation in old_translations:
            if translation not in approved_translations:
                translation.approved = False
                translation.approved_user = None
                translation.approved_date = None

                if translation.is_dirty():
                    self.translations_to_update.append(translation)

        # Any existing translations that are no longer fuzzy get unfuzzied.
        for translation in db_translations:
            if translation not in fuzzy_translations:
                translation.fuzzy = False

                if translation.is_dirty():
                    self.translations_to_update.append(translation)

    def prefetch_entity_translations(self):
        prefetched_entities = {}

        locale_entities = {}
        for locale_code, db_entity, vcs_entity in self.changes['update_db']:
            locale_entities.setdefault(locale_code, []).append(db_entity.pk)

        for locale in locale_entities.keys():
            entities_qs = Entity.objects.filter(
                pk__in=locale_entities[locale],
            ).prefetch_related(
                Prefetch(
                    'translation_set',
                    queryset=Translation.objects.filter(locale__code=locale),
                    to_attr='db_translations'
                )
            ).prefetch_related(
                Prefetch(
                    'translation_set',
                    queryset=Translation.objects.filter(locale__code=locale, approved_date__lte=self.now),
                    to_attr='old_translations'
                )
            )
            prefetched_entities[locale] = {entity.id: entity for entity in entities_qs}

        return prefetched_entities

    def execute_update_db(self):
        if self.changes['update_db']:
            entities_with_translations = self.prefetch_entity_translations()

        for locale_code, db_entity, vcs_entity in self.changes['update_db']:
            for field, value in self.get_entity_updates(vcs_entity).items():
                setattr(db_entity, field, value)

            if db_entity.is_dirty(check_relationship=True):
                self.entities_to_update.append(db_entity)

            if locale_code is not None:
                # Update translations for the entity.
                vcs_translation = vcs_entity.translations[locale_code]
                prefetched_entity = entities_with_translations[locale_code][db_entity.id]
                self.update_entity_translations_from_vcs(
                    db_entity, locale_code, vcs_translation, None,
                    prefetched_entity.db_translations, prefetched_entity.old_translations
                )

    def execute_obsolete_db(self):
        (Entity.objects
            .filter(pk__in=self.changes['obsolete_db'])
            .update(obsolete=True))

    def execute_obsolete_vcs_resources(self):
        for path in self.changes['obsolete_vcs_resources']:
            locales = [self.locale] if self.locale else self.db_project.locales.all()
            for locale in locales:
                locale_directory = self.vcs_project.locale_directory_paths[locale.code]
                file_path = os.path.join(locale_directory, path)
                if os.path.exists(file_path):
                    log.info('Removing obsolete file {} for {}.'.format(path, locale.code))
                    os.remove(file_path)
                    self.locales_to_commit.add(locale)

    def bulk_update_entities(self):
        if len(self.entities_to_update) > 0:
            bulk_update(self.entities_to_update, update_fields=[
                'resource',
                'string',
                'string_plural',
                'key',
                'comment',
                'order',
                'source'
            ])

    def bulk_create_translations(self):
        Translation.objects.bulk_create(self.translations_to_create)
        memory_entries = [TranslationMemoryEntry(
            source=t.entity.string,
            target=t.string,
            locale_id=t.locale_id,
            entity_id=t.entity.pk,
            translation_id=t.pk
        ) for t in self.translations_to_create if t.plural_form in (None, 0)]
        TranslationMemoryEntry.objects.bulk_create(memory_entries)

    def bulk_update_translations(self):
        if len(self.translations_to_update) > 0:
            bulk_update(self.translations_to_update, update_fields=[
                'entity',
                'locale',
                'string',
                'plural_form',
                'approved',
                'approved_user_id',
                'approved_date',
                'fuzzy',
                'extra'
            ])
