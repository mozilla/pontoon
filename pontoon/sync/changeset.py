from datetime import datetime

from django.utils import timezone

from bulk_update.helper import bulk_update

from pontoon.base.models import (
    Entity,
    Locale,
    Translation,
)
from pontoon.base.utils import match_attr


class ChangeSet(object):
    """
    Stores a set of changes to be made to the database and the
    translations stored in VCS. Once all the necessary changes have been
    stored, execute all the changes at once efficiently.
    """
    def __init__(self, db_project, vcs_project, now):
        """
        :param now:
            Datetime to use for marking when approvals happened.
        """
        self.db_project = db_project
        self.vcs_project = vcs_project
        self.now = now

        self.executed = False
        self.changes = {
            'update_vcs': [],
            'update_db': [],
            'obsolete_db': [],
            'create_db': []
        }

        self.entities_to_update = []
        self.translations_to_update = []
        self.translations_to_create = []

        self.commit_authors_per_locale = {}

    def update_vcs_entity(self, locale_code, db_entity, vcs_entity):
        """
        Replace the translations in VCS with the translations from the
        database.
        """
        self.changes['update_vcs'].append((locale_code, db_entity, vcs_entity))

    def create_db_entity(self, vcs_entity):
        """Create a new entity in the database."""
        self.changes['create_db'].append(vcs_entity)

    def update_db_entity(self, locale_code, db_entity, vcs_entity):
        """Update the database with translations from VCS."""
        self.changes['update_db'].append((locale_code, db_entity, vcs_entity))

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

        # Store locales and resources for FK relationships.
        self.locales = {l.code: l for l in Locale.objects.all()}
        self.resources = {r.path: r for r in self.db_project.resources.all()}

        # Perform the changes and fill the lists for bulk creation and
        # updating.
        self.execute_update_vcs()
        self.execute_create_db()
        self.execute_update_db()
        self.execute_obsolete_db()

        # Apply the built-up changes to the DB
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

        Translation.objects.bulk_create(self.translations_to_create)
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

    def execute_update_vcs(self):
        resources = self.vcs_project.resources
        changed_resources = set()

        for locale_code, db_entity, vcs_entity in self.changes['update_vcs']:
            changed_resources.add(resources[db_entity.resource.path])

            vcs_translation = vcs_entity.translations[locale_code]
            db_translations = (db_entity.translation_set
                               .filter(approved=True, locale__code=locale_code))

            # If no DB translations are fuzzy, set fuzzy to False.
            # Otherwise, it's true.
            vcs_translation.fuzzy = any(t for t in db_translations if t.fuzzy)

            if len(db_translations) > 0:
                last_translation = max(
                    db_translations,
                    key=lambda t: t.date or timezone.make_aware(datetime.min)
                )
                vcs_translation.last_updated = last_translation.date
                vcs_translation.last_translator = last_translation.user

            # Replace existing translations with ones from the database.
            vcs_translation.strings = {
                db.plural_form: db.string for db in db_translations
            }

            # Track which translators were involved.
            self.commit_authors_per_locale[locale_code] = [t.user for t in db_translations if t.user]

        for resource in changed_resources:
            resource.save()

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

    def execute_update_db(self):
        for locale_code, db_entity, vcs_entity in self.changes['update_db']:
            for field, value in self.get_entity_updates(vcs_entity).items():
                setattr(db_entity, field, value)

            if db_entity.is_dirty(check_relationship=True):
                self.entities_to_update.append(db_entity)

            # Update translations for the entity.
            vcs_translation = vcs_entity.translations[locale_code]
            db_translations = db_entity.translation_set.filter(
                locale__code=locale_code,
            )
            approved_translations = []

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
                    db_translation.fuzzy = vcs_translation.fuzzy
                    db_translation.extra = vcs_translation.extra

                    if db_translation.is_dirty():
                        self.translations_to_update.append(db_translation)
                    if not db_translation.fuzzy:
                        approved_translations.append(db_translation)
                else:
                    self.translations_to_create.append(Translation(
                        entity=db_entity,
                        locale=self.locales[locale_code],
                        string=string,
                        plural_form=plural_form,
                        approved=not vcs_translation.fuzzy,
                        approved_date=self.now if not vcs_translation.fuzzy else None,
                        fuzzy=vcs_translation.fuzzy,
                        extra=vcs_translation.extra
                    ))

            # Any existing translations that were not approved get unapproved.
            for translation in db_translations.filter(approved_date__lte=self.now):
                if translation not in approved_translations:
                    translation.approved = False
                    translation.approved_user = None
                    translation.approved_date = None

                    if translation.is_dirty():
                        self.translations_to_update.append(translation)

    def execute_obsolete_db(self):
        (Entity.objects
            .filter(pk__in=self.changes['obsolete_db'])
            .update(obsolete=True))
