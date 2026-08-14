import pytest

from pontoon.base.models.user import User
from pontoon.base.user_utils import can_translate
from pontoon.test.factories import ProjectLocaleFactory


@pytest.mark.django_db
def test_projectlocale_translators_group(project_a, locale_a, user_a: User):
    """
    Tests if user has permission to translate project at specific
    locale after assigment.
    """
    project_locale = ProjectLocaleFactory.create(
        project=project_a,
        locale=locale_a,
        has_custom_translators=True,
    )

    assert can_translate(user_a, project_a, locale_a) is False

    user_a.groups.add(project_locale.translators_group)
    assert can_translate(user_a, project_a, locale_a) is True

    project_locale.has_custom_translators = False
    project_locale.save()
    assert can_translate(user_a, project_a, locale_a) is False
