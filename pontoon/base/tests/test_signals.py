import pytest


@pytest.mark.django_db
def test_signal_base_project_locale_modified(project_locale_a, translation_a):
    """
    If ProjectLocale is modified (like setting the
    latest_translation), has_changed should not be modified.
    """
    project_locale_a.project.has_changed = False
    project_locale_a.project.save()
    project_locale_a.project.refresh_from_db()

    assert not project_locale_a.project.has_changed

    project_locale_a.latest_translation = None
    project_locale_a.project.save()
    project_locale_a.project.refresh_from_db()

    assert not project_locale_a.project.has_changed
    assert project_locale_a.latest_translation is None

    project_locale_a.latest_translation = translation_a
    project_locale_a.save()
    project_locale_a.project.refresh_from_db()

    assert not project_locale_a.project.has_changed
