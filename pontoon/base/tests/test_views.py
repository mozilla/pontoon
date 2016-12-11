from collections import OrderedDict
from datetime import (
    datetime,
    timedelta,
)

from random import randint

from django.http import HttpResponse
from django.shortcuts import render
from django.test import RequestFactory
from django.utils.timezone import now, make_aware

from django_nose.tools import (
    assert_equal,
    assert_true,
    assert_code,
)

from mock import patch

from pontoon.base.models import (
   Locale,
   Project,
   Entity,
   ProjectLocale,
   TranslatedResource,
   User,
)
from pontoon.base.utils import aware_datetime
from pontoon.base.tests import (
    assert_json,
    EntityFactory,
    LocaleFactory,
    ProjectFactory,
    ResourceFactory,
    TranslationFactory,
    TranslationMemoryFactory,
    TranslatedResourceFactory,
    TestCase,
    UserFactory,
)

from pontoon.base import views


def commajoin(*items):
    """
    Small helper function that joins all items by comma and maps types
    of items into strings.
    """
    return ','.join(map(str, items))


class UserTestCase(TestCase):
    """Default testcase for the views that require logged accounts."""
    def setUp(self):
        self.user = UserFactory.create()
        self.client.force_login(self.user)


class UserProfileTests(UserTestCase):
    """Tests related to the saving user profile."""
    def test_invalid_first_name(self):
        response = self.client.post('/save-user-name/', {'first_name': '<aa>"\'"'})

        assert_equal(response.status_code, 400)
        assert_equal(response.content, 'Enter a valid value.')

    def test_missing_first_name(self):
        response = self.client.post('/save-user-name/', {})

        assert_equal(response.status_code, 400)
        assert_equal(response.content, 'This field is required.')

    def test_valid_first_name(self):
        response = self.client.post('/save-user-name/', {'first_name': 'contributor'})

        assert_equal(response.status_code, 200)
        assert_equal(response.content, 'ok')

    def test_user_locales_order(self):
        locale1, locale2, locale3 = LocaleFactory.create_batch(3)
        response = self.client.get('/settings/')
        assert_equal(response.status_code, 200)

        response = self.client.post('/settings/', {
            'locales_order': commajoin(
                locale2.pk,
                locale1.pk,
                locale3.pk,
            )
        })

        assert_equal(response.status_code, 302)
        assert_equal(
            list(User.objects.get(pk=self.user.pk).profile.sorted_locales), [
                locale2,
                locale1,
                locale3,
            ]
        )
        # Test if you can clear all locales
        response = self.client.post('/settings/', {
            'locales_order': ''
        })
        assert_equal(response.status_code, 302)
        assert_equal(list(User.objects.get(pk=self.user.pk).profile.sorted_locales), [])


        # Test if form handles duplicated locales
        response = self.client.post('/settings/', {
            'locales_order': commajoin(
                locale1.pk,
                locale2.pk,
                locale2.pk,
            )
        })
        assert_equal(response.status_code, 302)
        assert_equal(
            list(User.objects.get(pk=self.user.pk).profile.sorted_locales), [
                locale1,
                locale2,
            ]
        )

class TranslationActionsTests(UserTestCase):
    """Tests actions that can be performed on a translation."""

    def setUp(self):
        super(TranslationActionsTests, self).setUp()
        project = ProjectFactory.create()
        locale = LocaleFactory.create()

        ProjectLocale.objects.create(project=project, locale=locale)

        translation = TranslationFactory.create(locale=locale, entity__resource__project=project)
        translation.approved = True
        translation.save()

        self.translation = translation

    def test_unapprove_translation(self):
        """Check if unapprove view works properly."""
        response = self.client.ajax_post('/unapprove-translation/', {
            'translation': self.translation.pk,
            'paths': [],
        })
        assert_code(response, 200)

        self.translation.refresh_from_db()
        assert_equal(self.translation.approved, False)
        assert_equal(self.translation.unapproved_user, self.user)


class TranslateTests(TestCase):
    def test_invalid_locale_and_project(self):
        """If the locale and project are both invalid, return a 404."""
        response = self.client.get('/invalid-locale/invalid-project/')
        assert_equal(response.status_code, 404)

    def test_invalid_locale_valid_project(self):
        """
        If the project is valid but the locale isn't, redirect home.
        """
        project = ProjectFactory.create(slug='valid-project')
        ResourceFactory.create(project=project)

        response = self.client.get('/invalid-locale/valid-project/path/')
        assert_equal(response.status_code, 404)

    def test_invalid_project(self):
        """If the project is invalid, redirect home."""
        LocaleFactory.create(code='fakelocale')

        response = self.client.get('/fakelocale/invalid-project/path/')
        assert_equal(response.status_code, 404)

    def test_locale_not_available(self):
        """
        If the requested locale is not available for this project,
        redirect home.
        """
        LocaleFactory.create(code='fakelocale')
        ProjectFactory.create(slug='valid-project')

        response = self.client.get('/fakelocale/valid-project/path/')
        assert_equal(response.status_code, 404)

    def test_not_authed_public_project(self):
        """
        If the user is not authenticated and we're translating project
        ID 1, return a 200.
        """
        # Clear out existing project with ID=1 if necessary.
        Project.objects.filter(id=1).delete()
        locale = LocaleFactory.create(code='fakelocale')
        project = ProjectFactory.create(id=1, slug='valid-project', locales=[locale])
        resource = ResourceFactory.create(project=project, path='foo.lang', total_strings=1)
        TranslatedResourceFactory.create(resource=resource, locale=locale)

        response = self.client.get('/fakelocale/valid-project/foo.lang/')
        assert_equal(response.status_code, 200)
        # I'd assertTemplateUsed here but it doesn't work on non-DTL
        # templates.


class ContributorProfileViewTests(UserTestCase):
    def setUp(self):
        super(ContributorProfileViewTests, self).setUp()

        mock_render = patch('pontoon.base.views.render', return_value=HttpResponse(''))
        self.mock_render = mock_render.start()
        self.addCleanup(mock_render.stop)

    def test_contributor_profile_by_username(self):
        """Users should be able to retrieve contributor's profile by its username."""
        self.client.get('/contributors/{}/'.format(self.user.username))

        assert_equal(self.mock_render.call_args[0][2]['contributor'], self.user)

    def test_contributor_profile_by_email(self):
        """Check if we can access contributor profile by its email."""
        self.client.get('/contributors/{}/'.format(self.user.email))

        assert_equal(self.mock_render.call_args[0][2]['contributor'], self.user)

    def test_logged_user_profile(self):
        """Logged user should be able to re"""
        self.client.get('/profile/')

        assert_equal(self.mock_render.call_args[0][2]['contributor'], self.user)

    def test_unlogged_user_profile(self):
        """Unlogged users shouldn't have access to edit any profile."""
        self.client.logout()

        assert_equal(self.client.get('/profile/')['Location'], '/403')


class ContributorTimelineViewTests(UserTestCase):
    """User timeline is a list of events created by a certain contributor."""
    def setUp(self):
        """
        We setup a sample contributor with random set of translations.
        """
        super(ContributorTimelineViewTests, self).setUp()
        self.project = ProjectFactory.create()
        self.translations = OrderedDict()

        for i in xrange(26):
            date = make_aware(datetime(2016, 12, 1) - timedelta(days=i))
            translations_count = randint(1,3)
            self.translations.setdefault((date, translations_count), []).append(
                TranslationFactory.create_batch(translations_count,
                    date=date,
                    user=self.user,
                    entity__resource__project=self.project,
                )
            )

        mock_render = patch('pontoon.base.views.render', return_value=HttpResponse(''))
        self.mock_render = mock_render.start()
        self.addCleanup(mock_render.stop)

    def test_timeline(self):
        """Backend should return events filtered by page number requested by user."""
        self.client.get('/contributors/{}/timeline/?page=2'.format(self.user.username))

        assert_equal(
            self.mock_render.call_args[0][2]['events'],
            [{
                'date': dt,
                'type': 'translation',
                'count': count,
                'project': self.project,
                'translation': translations[0][0],
            } for (dt,count), translations in self.translations.items()[10:20]
        ])

    def test_timeline_invalid_page(self):
        """Backend should return 404 error when user requests an invalid/empty page."""
        resp = self.client.get('/contributors/{}/timeline/?page=45'.format(self.user.username))
        assert_code(resp, 404)

        resp = self.client.get('/contributors/{}/timeline/?page=-aa45'.format(self.user.username))
        assert_code(resp, 404)

    def test_non_active_contributor(self):
        """Test if backend is able return events for a user without contributions."""
        nonactive_contributor = UserFactory.create()
        self.client.get('/contributors/{}/timeline/'.format(nonactive_contributor.username))
        assert_equal(
            self.mock_render.call_args[0][2]['events'], [
            {
                'date': nonactive_contributor.date_joined,
                'type': 'join'
            }
        ])

    def test_timeline_join(self):
        """Last page of results should include informations about the when user joined pontoon."""
        self.client.get('/contributors/{}/timeline/?page=3'.format(self.user.username))

        assert_equal(self.mock_render.call_args[0][2]['events'][-1], {
            'date': self.user.date_joined,
            'type': 'join'
        })


class ContributorsTests(TestCase):
    def setUp(self):
        mock_render = patch.object(views.ContributorsView, 'render_to_response', return_value=HttpResponse(''))
        self.mock_render = mock_render.start()
        self.addCleanup(mock_render.stop)

        mock_translations_manager = patch('pontoon.base.models.UserTranslationsManager.with_translation_counts')
        self.mock_translations_manager = mock_translations_manager.start()
        self.addCleanup(mock_translations_manager.stop)

    def test_default_period(self):
        """
        Calling the top contributors should result in period being None.
        """
        self.client.get('/contributors/')
        assert_true(self.mock_render.call_args[0][0]['period'] is None)
        assert_true(self.mock_translations_manager.call_args[0][0] is None)

    def test_invalid_period(self):
        """
        Checks how view handles invalid period, it result in period being None - displays all data.  """
        # If period parameter is invalid value
        self.client.get('/contributors/?period=invalidperiod')
        assert_true(self.mock_render.call_args[0][0]['period'] is None)
        assert_true(self.mock_translations_manager.call_args[0][0] is None)

        # Period shouldn't be negative integer
        self.client.get('/contributors/?period=-6')
        assert_true(self.mock_render.call_args[0][0]['period'] is None)
        assert_true(self.mock_translations_manager.call_args[0][0] is None)

    def test_given_period(self):
        """
        Checks if view sets and returns data for right period.
        """
        with patch('django.utils.timezone.now', wraps=now, return_value=aware_datetime(2015, 7, 5)):
            self.client.get('/contributors/?period=6')
            assert_equal(self.mock_render.call_args[0][0]['period'], 6)
            assert_equal(self.mock_translations_manager.call_args[0][0], aware_datetime(2015, 1, 5))


class ViewTestCase(TestCase):
    def setUp(self):
        """
        We don't call project synchronization during the tests, so we have to
        create dummy resource project to avoid recurse redirect at /.
        """
        ResourceFactory.create(project=Project.objects.get(pk=1))

        self.factory = RequestFactory()


class ProjectTests(ViewTestCase):
    def test_project_doesnt_exist(self):
        """
        Checks if view is returning error when project slug is invalid.
        """
        assert_code(self.client.get('/projects/project_doesnt_exist/'), 404)

    def test_project_view(self):
        """
        Checks if project page is returned properly.
        """
        project = ProjectFactory.create()
        ResourceFactory.create(project=project)

        with patch('pontoon.base.views.render', wraps=render) as mock_render:
            self.client.get('/projects/{}/'.format(project.slug))
            assert_equal(mock_render.call_args[0][2]['project'], project)


class ProjectContributorsTests(ViewTestCase):
    def test_project_doesnt_exist(self):
        """
        Checks if view handles invalid project.
        """
        assert_code(self.client.get('/projects/project_doesnt_exist/contributors/'), 404)

    def test_project_top_contributors(self):
        """
        Tests if view returns top contributors specific for given project.
        """
        first_project = ProjectFactory.create()
        ResourceFactory.create(project=first_project)
        first_project_contributor = TranslationFactory.create(entity__resource__project=first_project).user

        second_project = ProjectFactory.create()
        ResourceFactory.create(project=second_project)
        second_project_contributor = TranslationFactory.create(entity__resource__project=second_project).user

        with patch.object(views.ProjectContributorsView, 'render_to_response', return_value=HttpResponse('')) as mock_render:

            self.client.get('/projects/{}/contributors/'.format(first_project.slug))
            assert_equal(mock_render.call_args[0][0]['project'], first_project)
            assert_equal(list(mock_render.call_args[0][0]['contributors']), [first_project_contributor])

            self.client.get('/projects/{}/contributors/'.format(second_project.slug))
            assert_equal(mock_render.call_args[0][0]['project'], second_project)
            assert_equal(list(mock_render.call_args[0][0]['contributors']), [second_project_contributor])


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

        with patch('pontoon.base.views.render', wraps=render) as mock_render:
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
        first_locale_contributor = TranslationFactory.create(locale=first_locale,
            entity__resource__project__locales=[first_locale]).user

        second_locale = LocaleFactory.create()
        second_locale_contributor = TranslationFactory.create(locale=second_locale,
            entity__resource__project__locales=[second_locale]).user

        with patch.object(views.LocaleContributorsView, 'render_to_response', return_value=HttpResponse('')) as mock_render:
            self.client.get('/{}/contributors/'.format(first_locale.code))
            assert_equal(mock_render.call_args[0][0]['locale'], first_locale)
            assert_equal(list(mock_render.call_args[0][0]['contributors']), [first_locale_contributor])

            self.client.get('/{}/contributors/'.format(second_locale.code))
            assert_equal(mock_render.call_args[0][0]['locale'], second_locale)
            assert_equal(list(mock_render.call_args[0][0]['contributors']), [second_locale_contributor])


class LocaleProjectTests(ViewTestCase):
    def test_latest_activity(self):
        """Ensure that the latest_activity field is added to parts."""
        locale = LocaleFactory.create(code='test')
        project = ProjectFactory.create(locales=[locale], slug='test-project')
        resource = ResourceFactory.create(project=project, path='has/stats.po')
        translation = TranslationFactory.create(entity__resource=resource, locale=locale)
        TranslatedResourceFactory.create(resource=resource, locale=locale, latest_translation=translation)

        with patch.object(Locale, 'parts_stats') as mock_parts_stats, \
                patch('pontoon.base.views.render') as mock_render:
            mock_parts_stats.return_value = [
                {
                    'title': 'has/stats.po',
                    'resource__path': 'has/stats.po',
                    'resource__total_strings': 1,
                    'approved_strings': 0,
                    'translated_strings': 1,
                    'fuzzy_strings': 0,
                },
                {
                    'title': 'no/stats.po',
                    'resource__path': 'no/stats.po',
                    'resource__total_strings': 1,
                    'approved_strings': 0,
                    'translated_strings': 0,
                    'fuzzy_strings': 0,
                }
            ]

            views.locale_project(self.factory.get('/'), locale='test', slug='test-project')
            ctx = mock_render.call_args[0][2]
            assert_equal(ctx['parts'], [
                {
                    'latest_activity': translation.latest_activity,
                    'title': 'has/stats.po',
                    'resource__path': 'has/stats.po',
                    'resource__total_strings': 1,
                    'approved_strings': 0,
                    'translated_strings': 1,
                    'fuzzy_strings': 0,
                    'chart': {
                        'fuzzy_strings': 0,
                        'total_strings': 1,
                        'approved_strings': 0,
                        'translated_strings': 1,
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
                    'translated_strings': 0,
                    'fuzzy_strings': 0,
                    'chart': {
                        'fuzzy_strings': 0,
                        'total_strings': 1,
                        'approved_strings': 0,
                        'translated_strings': 0,
                        'approved_share': 0.0,
                        'translated_share': 0.0,
                        'fuzzy_share': 0.0,
                        'approved_percent': 0
                    }
                }
            ])


class TranslateMemoryTests(ViewTestCase):
    def test_best_quality_entry(self):
        """
        Translation memory should return results entries aggregated by
        translation string.
        """
        new_locale = LocaleFactory.create()
        memory_entry = TranslationMemoryFactory.create(source="aaa", target="ccc", locale=new_locale)
        TranslationMemoryFactory.create(source="aaa", target="ddd", locale=new_locale)
        TranslationMemoryFactory.create(source="bbb", target="ccc", locale=new_locale)

        response = self.client.get('/translation-memory/', {
            'text': 'aaa',
            'pk': memory_entry.entity.pk,
            'locale': new_locale.code
        })
        assert_json(response, [{"count": 1, "source": "aaa", "quality": 100.0, "target": "ddd"}])

    def test_translation_counts(self):
        """
        Translation memory should aggregate identical translations strings
        from the different entities and count up their occurrences.
        """
        new_locale = LocaleFactory.create()
        memory_entry = TranslationMemoryFactory.create(source="aaaa", target="ccc", locale=new_locale)
        TranslationMemoryFactory.create(source="abaa", target="ccc", locale=new_locale)
        TranslationMemoryFactory.create(source="aaab", target="ccc", locale=new_locale)
        TranslationMemoryFactory.create(source="aaab", target="ccc", locale=new_locale)

        response = self.client.get('/translation-memory/', {
            'text': 'aaaa',
            'pk': memory_entry.entity.pk,
            'locale': memory_entry.locale.code
        })
        assert_json(response, [{u'count': 3,
                     u'quality': 75.0,
                     u'source': u'abaa',
                     u'target': u'ccc'}])

    def test_exclude_entity(self):
        """
        Exclude entity from results to avoid false positive results.
        """
        memory_entry = TranslationMemoryFactory.create(source="Pontoon Intro")
        response = self.client.get('/translation-memory/', {
            'text': 'Pontoon Intro',
            'pk': memory_entry.entity.pk,
            'locale': memory_entry.locale.code
        })
        assert_code(response, 200)
        assert_equal(response.content, '[]')

    def test_minimal_quality(self):
        """
        View shouldn't return any entries if 70% of quality at minimum.
        """
        # Generate some random entries that shouldn't be similar
        TranslationMemoryFactory.create_batch(5)

        response = self.client.get('/translation-memory/', {
            'text': 'no match',
            'pk': 2,
            'locale': 'en-GB'
        })
        assert_code(response, 200)
        assert_equal(response.content, '[]')


class EntityViewTests(TestCase):
    """
    Tests related to the get_entity view.
    """

    def setUp(self):
        self.resource = ResourceFactory.create()
        self.locale = LocaleFactory.create()
        ProjectLocale.objects.create(project=self.resource.project, locale=self.locale)
        TranslatedResource.objects.create(resource=self.resource, locale=self.locale)
        self.entities = EntityFactory.create_batch(3, resource=self.resource)
        self.entities_pks = [e.pk for e in self.entities]

    def test_inplace_mode(self):
        """
        Inplace mode of get_entites, should return all entities in a single batch.
        """
        response = self.client.ajax_post('/get-entities/', {
            'project': self.resource.project.slug,
            'locale': self.locale.code,
            'paths[]': [self.resource.path],
            'inplaceEditor': True,
            # Inplace mode shouldn't respect paging or limiting page
            'limit': 1,
        })

        assert_code(response, 200)
        assert_equal(response.json()['has_next'], False)
        assert_equal([e['pk'] for e in response.json()['entities']], self.entities_pks)

    def test_entity_filters(self):
        """
        Tests if right filter calls right method in the Entity manager.
        """
        filters = (
            'missing',
            'fuzzy',
            'suggested',
            'translated',
            'unchanged',
            'has-suggestions',
        )

        for filter_ in filters:
            filter_name = filter_.replace('-', '_')
            params = {
                'project': self.resource.project.slug,
                'locale': self.locale.code,
                'paths[]': [self.resource.path],
                'limit': 1,
            }

            if filter_ == 'unchanged' or filter_ == 'has-suggestions':
                params['extra'] = filter_

            else:
                params['status'] = filter_

            with patch('pontoon.base.models.Entity.objects.{}'.format(filter_name), return_value=getattr(Entity.objects, filter_name)()) as filter_mock:
                self.client.ajax_post('/get-entities/', params)
                assert_true(filter_mock.called)

    def test_exclude_entities(self):
        """
        Excluded entities shouldn't returned by get_entities.
        """
        response = self.client.ajax_post('/get-entities/', {
            'project': self.resource.project.slug,
            'locale': self.locale.code,
            'paths[]': [self.resource.path],
            'excludeEntities[]': [self.entities[1].pk],
            'limit': 1,
        })

        assert_code(response, 200)

        assert_equal(response.json()['has_next'], True)
        assert_equal([e['pk'] for e in response.json()['entities']], [self.entities[0].pk,])

        response = self.client.ajax_post('/get-entities/', {
            'project': self.resource.project.slug,
            'locale': self.locale.code,
            'paths[]': [self.resource.path],
            'excludeEntities[]': [self.entities[0].pk, self.entities[1].pk],
            'limit': 1,
        })

        assert_code(response, 200)

        assert_equal(response.json()['has_next'], False)
        assert_equal([e['pk'] for e in response.json()['entities']], [self.entities[2].pk])
