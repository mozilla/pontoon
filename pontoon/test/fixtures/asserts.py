import pytest


@pytest.fixture
def assert_permissionchangelog():
    """
    Shortcut assert function for freshly created permission changeset objects.
    """

    def _assert(changelog_item, action_type, performed_by, performed_on, group):
        assert changelog_item.action_type == action_type
        assert changelog_item.performed_by == performed_by
        assert changelog_item.performed_on == performed_on
        assert changelog_item.group == group

    return _assert
