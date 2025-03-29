import uuid

from unittest.mock import patch

import pytest

from django.test.client import RequestFactory

from pontoon.messaging.emails import send_verification_email


# Test that the verification email is sent correctly.
@pytest.mark.django_db
def test_send_verification_email(member):
    with patch("pontoon.messaging.emails.EmailMultiAlternatives") as mock_email_message:
        rf = RequestFactory()
        request = rf.get("/settings/")
        request.user = member.user

        link = "EMAIL-VERIFICATION-LINK"
        send_verification_email(request.user, link)
        assert mock_email_message.called

        kwargs = mock_email_message.call_args.kwargs
        assert link in kwargs["body"]
        assert kwargs["to"] == [request.user.email]


# Test that the classification logic correctly categorizes users.
@pytest.mark.django_db
def test_locale_contributor_classification():
    # Dummy user class for testing classification.
    class DummyUser:
        def __init__(self, pk, is_staff, email):
            self.pk = pk
            self.is_staff = is_staff
            self.email = email

        def __eq__(self, other):
            return isinstance(other, DummyUser) and self.pk == other.pk

        def __hash__(self):
            return hash(self.pk)

    # Create dummy users.
    manager = DummyUser("manager1", False, "manager1@example.com")
    translator = DummyUser("translator1", False, "translator1@example.com")
    contributor = DummyUser("contributor1", False, "contributor1@example.com")
    users_dict = {
        "manager1": manager,
        "translator1": translator,
        "contributor1": contributor,
    }

    # Dummy classes to simulate locale groups.
    class DummyGroup:
        def __init__(self, managers=None, translators=None):
            self.fetched_managers = managers or []
            self.fetched_translators = translators or []

    class DummyLocale:
        def __init__(self, pk, managers, translators):
            self.pk = pk
            self.managers_group = DummyGroup(managers, [])
            self.translators_group = DummyGroup([], translators)

    # Create a unique locale and assign groups.
    unique_code = f"te_test_{uuid.uuid4().hex[:4]}"
    dummy_locale = DummyLocale(unique_code, [manager], [translator])

    # Simulated monthly_contributors data.
    monthly_contributors = [
        {"translation__locale": unique_code, "performed_by": "manager1"},
        {"translation__locale": unique_code, "performed_by": "translator1"},
        {"translation__locale": unique_code, "performed_by": "contributor1"},
    ]
    # Mark contributor as new.
    new_locale_contributors = {(unique_code, "contributor1")}

    new_contributors = []
    active_managers = []
    active_translators = []
    active_contributors = []

    for entry in monthly_contributors:
        user_pk = entry["performed_by"]
        user = users_dict.get(user_pk)

        if (unique_code, user_pk) in new_locale_contributors:
            if not user.is_staff:
                new_contributors.append(user)
            continue

        if user in dummy_locale.managers_group.fetched_managers:
            active_managers.append(user)
        elif user in dummy_locale.translators_group.fetched_translators:
            active_translators.append(user)
        else:
            active_contributors.append(user)

    # Assert the expected categorization.
    assert new_contributors == [contributor]
    assert active_managers == [manager]
    assert active_translators == [translator]
    assert active_contributors == []
