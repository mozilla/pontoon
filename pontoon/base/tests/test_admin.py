"""
Tests related to all admin code
"""

from pontoon.base.admin import UserAdmin
from pontoon.base.tests import TestCase


class UserAdminUserRoleLogTests(TestCase):
    """
    Check if admin form saves logs of changes on users groups they are
    assigned to.
    """
    def test_add_user_to_group(self):
        # Check idempotency
        assert False

    def test_remove_user_from_group(self):
        assert False
