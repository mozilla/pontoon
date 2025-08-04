from pontoon.checks.libraries.translate_toolkit import run_checks


def test_tt_invalid_translation():
    """
    Check if translate toolkit returns errors if chek
    """
    assert run_checks(
        "Original string",
        "Translation \\q",
        "en-US",
    ) == {"ttWarnings": ["Escapes"]}


def test_tt_disabled_checks():
    """
    Disabled checks should be respected by the run_checks.
    """
    assert (
        run_checks(
            "Original string",
            "Translation \\q",
            "en-US",
            disabled_checks={"escapes"},
        )
        == {}
    )


def test_tt_correct_translation():
    """
    Quality check should return empty dictionary if everything is okay (no warnings).
    """
    assert run_checks("Original string", "Translation string", "en-US") == {}
