from unittest.mock import patch

import pytest

from pontoon.base.tests import (
    EntityFactory,
    ResourceFactory,
    TranslationFactory,
)
from pontoon.sync.core import notify_users


@patch("pontoon.messaging.notifications.notify.send")
@pytest.mark.django_db
def test_notify_users_excludes_system_users(
    mock_notify, locale_a, project_a, project_locale_a, user_a, tm_user
):
    """System users that authored translations in a project must not be
    notified about new strings landing in that project."""
    resource = ResourceFactory.create(project=project_a)
    entity = EntityFactory.create(resource=resource)

    TranslationFactory.create(locale=locale_a, entity=entity, user=user_a)
    TranslationFactory.create(locale=locale_a, entity=entity, user=tm_user)

    notify_users(project_a, count=1)

    recipients = {call.kwargs["recipient"] for call in mock_notify.call_args_list}
    assert user_a in recipients
    assert tm_user not in recipients
