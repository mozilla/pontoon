import pytest


@pytest.mark.django_db
def test_signal_base_project_modified(project_a):
    start_time = project_a.date_modified

    project_a.configuration_file = "test.toml"
    project_a.save()
    project_a.refresh_from_db()
    assert project_a.date_modified != start_time


@pytest.mark.django_db
def test_signal_base_project_locale_modified(
    project_a, project_locale_a, translation_a
):
    """
    If ProjectLocale is modified (like setting the
    latest_translation), has_changed should not be modified.
    """
    start_time = project_a.date_modified

    project_locale_a.project.has_changed = False
    project_locale_a.project.save()
    project_locale_a.project.refresh_from_db()

    assert not project_locale_a.project.has_changed

    project_locale_a.latest_translation = None
    project_locale_a.project.save()
    project_locale_a.project.refresh_from_db()

    assert not project_locale_a.project.has_changed
    assert project_locale_a.latest_translation is None

    # Toggling the value should set project.date_modified on the next save()
    project_locale_a.pretranslation_enabled = True

    project_locale_a.latest_translation = translation_a
    project_locale_a.save()
    project_locale_a.project.refresh_from_db()

    assert not project_locale_a.project.has_changed
    assert project_a.date_modified != start_time
