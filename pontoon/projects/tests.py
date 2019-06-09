from __future__ import absolute_import

from django.http import HttpResponse
from django.shortcuts import render

from django_nose.tools import (
    assert_equal,
    assert_code,
)

from mock import patch

from pontoon.base.tests import (
    ProjectFactory,
    ResourceFactory,
    TranslationFactory,
)

from pontoon.base.tests.test_views import ViewTestCase
from pontoon.projects import views


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

        with patch('pontoon.projects.views.render', wraps=render) as mock_render:
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
        first_project_contributor = (
            TranslationFactory.create(entity__resource__project=first_project).user
        )

        second_project = ProjectFactory.create()
        ResourceFactory.create(project=second_project)
        second_project_contributor = (
            TranslationFactory.create(entity__resource__project=second_project).user
        )

        with patch.object(
            views.ProjectContributorsView, 'render_to_response', return_value=HttpResponse('')
        ) as mock_render:
            self.client.get(
                '/projects/{}/ajax/contributors/'.format(first_project.slug),
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            assert_equal(mock_render.call_args[0][0]['project'], first_project)
            assert_equal(
                list(mock_render.call_args[0][0]['contributors']),
                [first_project_contributor]
            )

            self.client.get(
                '/projects/{}/ajax/contributors/'.format(second_project.slug),
                HTTP_X_REQUESTED_WITH='XMLHttpRequest'
            )
            assert_equal(mock_render.call_args[0][0]['project'], second_project)
            assert_equal(
                list(mock_render.call_args[0][0]['contributors']),
                [second_project_contributor]
            )
