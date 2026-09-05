import pytest

from pontoon.base.models import Resource, Translation
from pontoon.checks.models import (
    Error,
    FailedCheck,
    Warning,
)
from pontoon.checks.utils import (
    bulk_run_checks,
    get_failed_checks_db_objects,
    save_failed_checks,
)


@pytest.fixture()
def translation_properties(translation_a):
    resource = translation_a.entity.resource
    resource.path = "test.properties"
    resource.format = Resource.Format.PROPERTIES
    resource.save()

    yield translation_a


@pytest.fixture
def translation_compare_locales_warning(translation_properties):
    # Create new instance
    translation = Translation.objects.get(pk=translation_properties.pk)
    translation.pk = None

    translation.string = "raise warning \\q"
    translation.save()

    yield translation


@pytest.fixture
def translation_compare_locales_error(translation_properties):
    # Create new instance
    translation = Translation.objects.get(pk=translation_properties.pk)
    translation.pk = None

    entity = translation.entity
    entity.string = "test %s %s"
    entity.save()

    translation.string = "raise error %"
    translation.save()

    yield translation


@pytest.fixture
def translation_pontoon_warning(translation_a):
    """
    An Android translation that drops a placeholder used by the source string
    """
    resource = translation_a.entity.resource
    resource.path = "strings.xml"
    resource.format = Resource.Format.ANDROID
    resource.save()

    entity = translation_a.entity
    entity.string = "Source string with a {$arg1 :string @source=|%1$s|}"
    entity.save()

    # Create new instance
    translation = Translation.objects.get(pk=translation_a.pk)
    translation.pk = None

    translation.string = "Translation without the placeholder"
    translation.save()

    yield translation


@pytest.fixture
def translation_pontoon_error(translation_a):
    # Create new instance
    translation = Translation.objects.get(pk=translation_a.pk)
    translation.pk = None

    resource = translation.entity.resource
    resource.path = "test.po"
    resource.format = Resource.Format.GETTEXT
    resource.save()

    translation.string = ""
    translation.save()
    yield translation


@pytest.mark.django_db
def test_save_failed_checks(translation_a):
    save_failed_checks(
        translation_a,
        {
            "clErrors": ["compare-locales error 1", "compare-locales error 2"],
            "clWarnings": ["compare-locales warning 1"],
            "pWarnings": ["pontoon warning 1"],
            # Warnings from Translate Toolkit can't be stored in the Database
            "ttWarnings": [
                "translate-toolkit warning 1",
                "translate-toolkit warning 2",
            ],
            # Neither can Pontoon's non-DB warnings
            "pndbWarnings": ["Empty translation"],
        },
    )

    error1, error2 = Error.objects.order_by("message")

    assert error1.library == FailedCheck.Library.COMPARE_LOCALES
    assert error1.message == "compare-locales error 1"
    assert error2.library == FailedCheck.Library.COMPARE_LOCALES
    assert error2.message == "compare-locales error 2"

    cl_warning, p_warning = Warning.objects.order_by("library", "message")

    assert cl_warning.library == FailedCheck.Library.COMPARE_LOCALES
    assert cl_warning.message == "compare-locales warning 1"

    assert p_warning.library == FailedCheck.Library.PONTOON
    assert p_warning.message == "pontoon warning 1"


@pytest.mark.django_db
def test_save_no_checks(translation_a):
    save_failed_checks(translation_a, {})
    assert not Warning.objects.all().exists()
    assert not Error.objects.all().exists()


@pytest.mark.django_db
def test_bulk_run_checks_no_translations():
    """
    Don't generate any warnings and errors without translations
    """
    assert bulk_run_checks([]) is None

    assert Warning.objects.count() == 0
    assert Error.objects.count() == 0


@pytest.mark.django_db
def test_bulk_run_checks(
    translation_compare_locales_warning,
    translation_compare_locales_error,
    translation_pontoon_error,
):
    warnings, errors = bulk_run_checks(
        [
            translation_compare_locales_warning,
            translation_pontoon_error,
            translation_compare_locales_error,
        ]
    )

    (cl_warning,) = warnings
    p_error, cl_error = errors

    assert cl_warning.pk is not None
    assert cl_warning.library == FailedCheck.Library.COMPARE_LOCALES
    assert cl_warning.message == "unknown escape sequence, \\q"
    assert cl_warning.translation == translation_compare_locales_warning

    assert cl_error.pk is not None
    assert cl_error.library == FailedCheck.Library.COMPARE_LOCALES
    assert cl_error.message == "Found single %"
    assert cl_error.translation == translation_compare_locales_error

    assert p_error.pk is not None
    assert p_error.library == FailedCheck.Library.PONTOON
    assert p_error.message == "Empty translations are not allowed"
    assert p_error.translation == translation_pontoon_error


@pytest.mark.django_db
def test_bulk_run_checks_pontoon_warning(translation_pontoon_warning):
    """
    Warnings raised by Pontoon's own checks must be stored
    """
    warnings, errors = bulk_run_checks([translation_pontoon_warning])

    assert errors == []

    (p_warning,) = warnings
    assert p_warning.pk is not None
    assert p_warning.library == FailedCheck.Library.PONTOON
    assert p_warning.message == "Placeholder %1$s not found in translation"
    assert p_warning.translation == translation_pontoon_warning

    assert translation_pontoon_warning.warnings.count() == 1


@pytest.mark.django_db
def test_unknown_library_is_logged(translation_a, caplog):
    """
    Failed checks with an unrecognised library prefix are not dropped silently
    """
    warnings, errors = get_failed_checks_db_objects(
        translation_a, {"nopeWarnings": ["dropped warning"]}
    )

    assert (warnings, errors) == ([], [])
    assert "unknown library 'nope'" in caplog.text


@pytest.mark.django_db
def test_get_failed_checks_db_objects(translation_a):
    """
    Return model instances of warnings and errors
    """
    warnings, errors = get_failed_checks_db_objects(
        translation_a,
        {
            "clWarnings": ["compare-locales warning 1"],
            "pWarnings": ["pontoon warning 1"],
            # Warnings from some libraries e.g. Translate Toolkit, shouldn't land in the database.
            "ttWarnings": ["translate-toolkit warning 1"],
            "pndbWarnings": ["Empty translation"],
            "clErrors": ["compare-locales error 1"],
            "pErrors": ["pontoon error 1"],
        },
    )

    # Check if objects aren't saved in DB
    assert all([w.pk is None for w in warnings])
    assert all([e.pk is None for e in errors])

    cl_warning, p_warning = sorted(warnings, key=lambda w: w.library)
    cl_error, p_error = sorted(errors, key=lambda e: e.library)

    assert cl_warning.library == FailedCheck.Library.COMPARE_LOCALES
    assert cl_warning.message == "compare-locales warning 1"
    assert cl_warning.translation == translation_a

    assert p_warning.library == FailedCheck.Library.PONTOON
    assert p_warning.message == "pontoon warning 1"
    assert p_warning.translation == translation_a

    assert cl_error.library == FailedCheck.Library.COMPARE_LOCALES
    assert cl_error.message == "compare-locales error 1"
    assert cl_error.translation == translation_a

    assert p_error.library == FailedCheck.Library.PONTOON
    assert p_error.message == "pontoon error 1"
    assert p_error.translation == translation_a
