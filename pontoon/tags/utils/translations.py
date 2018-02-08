
from django.db.models import Max, Q

from .base import TagsTRTool


class TagsLatestTranslationsTool(TagsTRTool):
    """For given filters this tool will find the latest ``Translations``
    for a ``Tag``. It uses TranslatedResources to find the translations
    but returns translations.
    """
    filter_methods = ('tag', 'projects', 'latest', 'locales', 'path')

    _default_annotations = (
        ('last_change', Max('latest_translation__date')), )

    @property
    def groupby_prefix(self):
        # as we find latest_translations for translated_resources
        # and use that to retrieve the translations, we need to map the groupby
        # field here
        groupby = list(self.get_groupby())
        if groupby == ['resource__tag']:
            return "entity__resource__tag"
        elif groupby == ['locale']:
            return "locale"

    def coalesce(self, data):
        return {
            translation[self.groupby_prefix]: translation
            for translation
            in data.iterator()}

    def get_data(self):
        _translations = self.translation_manager.none()
        stats = super(TagsLatestTranslationsTool, self).get_data()
        for tr in stats.iterator():
            # find translations with matching date and tag/locale
            _translations |= self.translation_manager.filter(
                Q(**{'date': tr["last_change"],
                     self.groupby_prefix: tr[self.get_groupby()[0]]}))
        return _translations.values(
            *('string',
              'date',
              'approved_date',
              'user__first_name',
              'user__email')
            + (self.groupby_prefix, ))

    def filter_latest(self, qs):
        return qs.exclude(latest_translation__isnull=True)
