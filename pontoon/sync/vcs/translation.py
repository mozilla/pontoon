from datetime import datetime

from django.utils import timezone


class VCSTranslation:
    """
    A single translation of a source string into another language.

    Since a string can have different translations based on plural
    forms, all of the different forms are stored under self.strings, a
    dict where the keys equal possible values for
    pontoon.base.models.Translation.plural_form and the values equal the
    translation for that plural form.
    """

    def __init__(
        self,
        key,
        strings,
        comments,
        fuzzy,
        context="",
        source_string="",
        source_string_plural="",
        group_comments=None,
        resource_comments=None,
        order=0,
        source=None,
        last_translator=None,
        last_updated=None,
    ):
        self.key = key
        self.context = context
        self.source_string = source_string
        self.source_string_plural = source_string_plural
        self.strings = strings
        self.comments = comments
        self.group_comments = group_comments
        self.resource_comments = resource_comments
        self.fuzzy = fuzzy
        self.order = order
        self.source = source or []
        self.last_translator = last_translator
        self.last_updated = last_updated

    def update_from_db(self, db_translations):
        """
        Update translation with current DB state.
        """
        # If no DB translations are fuzzy, set fuzzy to False.
        # Otherwise, it's true.
        self.fuzzy = any(t for t in db_translations if t.fuzzy)

        if len(db_translations) > 0:
            last_translation = max(
                db_translations,
                key=lambda t: t.date or timezone.make_aware(datetime.min),
            )
            self.last_updated = last_translation.date
            self.last_translator = last_translation.user

        # Replace existing translations with ones from the database.
        self.strings = {db.plural_form: db.string for db in db_translations}
