from django.http import HttpResponse
from django.shortcuts import render

from django_nose.tools import (
    assert_equal,
    assert_code,
)

from mock import patch

from pontoon.base.tests import (
    LocaleFactory,
    ResourceFactory,
    TranslationFactory,
)

from pontoon.base.tests.test_views import ViewTestCase
from pontoon.teams import views


class LocaleTests(ViewTestCase):
    def test_locale_doesnt_exist(self):
        """
        Tests if view is returning an error on the missing locale.
        """
        assert_code(self.client.get('/missing-locale/'), 404)

    def test_locale_view(self):
        """
        Checks if locale page is returned properly.
        """
        locale = LocaleFactory.create()

        # Locale requires valid project with resources
        ResourceFactory.create(project__locales=[locale])

        with patch('pontoon.teams.views.render', wraps=render) as mock_render:
            self.client.get('/{}/'.format(locale.code))
            assert_equal(mock_render.call_args[0][2]['locale'], locale)


class LocaleContributorsTests(ViewTestCase):
    def test_locale_doesnt_exist(self):
        """
        Tests if view is returning an error on the missing locale.
        """
        assert_code(self.client.get('/missing-locale/contributors/'), 404)

    def test_locale_top_contributors(self):
        """
        Tests if view returns top contributors specific for given locale.
        """
        first_locale = LocaleFactory.create()
        first_locale_contributor = TranslationFactory.create(
            locale=first_locale,
            entity__resource__project__locales=[first_locale]
        ).user

        second_locale = LocaleFactory.create()
        second_locale_contributor = TranslationFactory.create(
            locale=second_locale,
            entity__resource__project__locales=[second_locale]
        ).user

        with patch.object(
            views.LocaleContributorsView, 'render_to_response', return_value=HttpResponse('')
        ) as mock_render:
            self.client.get(
                '/{}/ajax/contributors/'.format(first_locale.code),
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            assert_equal(mock_render.call_args[0][0]['locale'], first_locale)
            assert_equal(
                list(mock_render.call_args[0][0]['contributors']),
                [first_locale_contributor]
            )

            self.client.get(
                '/{}/ajax/contributors/'.format(second_locale.code),
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            assert_equal(mock_render.call_args[0][0]['locale'], second_locale)
            assert_equal(
                list(mock_render.call_args[0][0]['contributors']),
                [second_locale_contributor]
            )
