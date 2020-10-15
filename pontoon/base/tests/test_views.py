from django.test import RequestFactory

from pontoon.base.models import Project

from pontoon.base.tests import TestCase
from pontoon.test.factories import (
    ResourceFactory,
    UserFactory,
)


class UserTestCase(TestCase):
    """Default testcase for the views that require logged accounts."""

    def setUp(self):
        self.user = UserFactory.create()
        self.client.force_login(self.user)


class ViewTestCase(TestCase):
    def setUp(self):
        """
        We don't call project synchronization during the tests, so we have to
        create dummy resource project to avoid recurse redirect at /.
        """
        ResourceFactory.create(project=Project.objects.get(pk=1))

        self.factory = RequestFactory()
