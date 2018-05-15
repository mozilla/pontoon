
import pytest


@pytest.mark.django_db
def test_signal_base_project_locale_modified(project_locale0, translation0):
    """
    If ProjectLocale is modified (like setting the
    latest_translation), has_changed should not be modified.
    """
    project_locale0.project.has_changed = False
    project_locale0.project.save()
    project_locale0.project.refresh_from_db()
    assert not project_locale0.project.has_changed
    project_locale0.latest_translation = None
    project_locale0.project.save()
    project_locale0.project.refresh_from_db()
    assert not project_locale0.project.has_changed
    assert project_locale0.latest_translation is None
    project_locale0.latest_translation = translation0
    project_locale0.save()
    project_locale0.project.refresh_from_db()
    assert not project_locale0.project.has_changed
