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

