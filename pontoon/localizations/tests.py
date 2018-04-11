from django_nose.tools import assert_equal
from mock import patch

from pontoon.base.models import Locale
from pontoon.base.tests import (
    LocaleFactory,
    ProjectFactory,
    ResourceFactory,
    TranslationFactory,
    TranslatedResourceFactory,
)
from pontoon.base.tests.test_views import ViewTestCase
from pontoon.localizations import views


class LocaleProjectTests(ViewTestCase):
    def test_latest_activity(self):
        """Ensure that the latest_activity field is added to parts."""
        locale = LocaleFactory.create(code='test')
        project = ProjectFactory.create(locales=[locale], slug='test-project')
        resource = ResourceFactory.create(project=project, path='has/stats.po')
        resource2 = ResourceFactory.create(project=project, path='has/stats2.po')

        translation = TranslationFactory.create(entity__resource=resource, locale=locale)
        TranslatedResourceFactory.create(
            resource=resource2, locale=locale, latest_translation=translation
        )

        with patch.object(Locale, 'parts_stats') as mock_parts_stats, \
                patch('pontoon.localizations.views.render') as mock_render:
            mock_parts_stats.return_value = [
                {
                    'title': 'has/stats.po',
                    'resource__path': 'has/stats.po',
                    'resource__total_strings': 1,
                    'approved_strings': 0,
                    'unreviewed_strings': 1,
                    'fuzzy_strings': 0,
                },
                {
                    'title': 'no/stats.po',
                    'resource__path': 'no/stats.po',
                    'resource__total_strings': 1,
                    'approved_strings': 0,
                    'unreviewed_strings': 0,
                    'fuzzy_strings': 0,
                }
            ]
            views.ajax_resources(
                self.factory.get('/', HTTP_X_REQUESTED_WITH='XMLHttpRequest'),
                code=locale.code,
                slug=project.slug
            )
            ctx = mock_render.call_args[0][2]
            assert_equal(ctx['resources'], [
                {
                    'latest_activity': translation.latest_activity,
                    'title': 'has/stats.po',
                    'resource__path': 'has/stats.po',
                    'resource__total_strings': 1,
                    'approved_strings': 0,
                    'unreviewed_strings': 1,
                    'fuzzy_strings': 0,
                    'chart': {
                        'fuzzy_strings': 0,
                        'total_strings': 1,
                        'approved_strings': 0,
                        'unreviewed_strings': 1,
                        'approved_share': 0.0,
                        'translated_share': 100.0,
                        'fuzzy_share': 0.0,
                        'approved_percent': 0
                    }
                },
                {
                    'latest_activity': None,
                    'title': 'no/stats.po',
                    'resource__path': 'no/stats.po',
                    'resource__total_strings': 1,
                    'approved_strings': 0,
                    'unreviewed_strings': 0,
                    'fuzzy_strings': 0,
                    'chart': {
                        'fuzzy_strings': 0,
                        'total_strings': 1,
                        'approved_strings': 0,
                        'unreviewed_strings': 0,
                        'approved_share': 0.0,
                        'translated_share': 0.0,
                        'fuzzy_share': 0.0,
                        'approved_percent': 0
                    }
                }
            ])
