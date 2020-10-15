import pytest

from django.core.exceptions import ValidationError

from pontoon.actionlog import utils
from pontoon.actionlog.models import ActionLog


@pytest.mark.django_db
def test_log_action_missing_arg(user_a, entity_a, locale_a):
    # No translation nor (entity and locale) pair.
    with pytest.raises(ValidationError):
        utils.log_action("translation:created", user_a)

    # Missing locale.
    with pytest.raises(ValidationError):
        utils.log_action("translation:deleted", user_a, entity=entity_a)

    # Missing entity.
    with pytest.raises(ValidationError):
        utils.log_action("translation:deleted", user_a, locale=locale_a)


@pytest.mark.django_db
def test_log_action_unknown_action_type(user_a, translation_a):
    # We send an unsupported action type.
    with pytest.raises(ValidationError):
        utils.log_action(
            "test:unknown", user_a, translation=translation_a,
        )


@pytest.mark.django_db
def test_log_action_deleted_wrong_keys(user_a, translation_a):
    # We send the wrong parameters for the "deleted" action.
    with pytest.raises(ValidationError):
        utils.log_action(
            "translation:deleted", user_a, translation=translation_a,
        )


@pytest.mark.django_db
def test_log_action_non_deleted_wrong_keys(user_a, entity_a, locale_a):
    # We send the wrong parameters for a non-"deleted" action.
    with pytest.raises(ValidationError):
        utils.log_action(
            "translation:approved", user_a, entity=entity_a, locale=locale_a,
        )


@pytest.mark.django_db
def test_log_action_valid_with_translation(user_a, translation_a):
    utils.log_action(
        "translation:created", user_a, translation=translation_a,
    )

    log = ActionLog.objects.filter(performed_by=user_a, translation=translation_a)
    assert len(log) == 1
    assert log[0].action_type == "translation:created"


@pytest.mark.django_db
def test_log_action_valid_with_entity_locale(user_a, entity_a, locale_a):
    utils.log_action(
        "translation:deleted", user_a, entity=entity_a, locale=locale_a,
    )

    log = ActionLog.objects.filter(
        performed_by=user_a, entity=entity_a, locale=locale_a,
    )
    assert len(log) == 1
    assert log[0].action_type == "translation:deleted"
