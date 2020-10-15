import pytest

from pontoon.checks.libraries.translate_toolkit import run_checks


@pytest.yield_fixture()
def mock_locale():
    """Small mock of Locale object to make faster unit-tests."""
    yield "en-US"


def test_tt_invalid_translation(mock_locale):
    """
    Check if translate toolkit returns errors if chek
    """
    assert run_checks("Original string", "Translation \\q", mock_locale,) == {
        "ttWarnings": ["Escapes"]
    }


def test_tt_disabled_checks(mock_locale):
    """
    Disabled checks should be respected by the run_checks.
    """
    assert (
        run_checks(
            "Original string",
            "Translation \\q",
            mock_locale,
            disabled_checks={"escapes"},
        )
        == {}
    )


def test_tt_correct_translation(mock_locale):
    """
    Quality check should return empty dictionary if everything is okay (no warnings).
    """
    assert run_checks("Original string", "Translation string", mock_locale) == {}
