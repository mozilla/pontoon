from pontoon.insights.utils import get_chrf_score


def test_get_chrf_score_none():
    """A NULL score (no activity) should return None."""
    assert get_chrf_score({"pretranslations_chrf_score_avg": None}) is None


def test_get_chrf_score_zero():
    """A score of 0.0 is a valid chrF++ result and should not be treated as None."""
    assert get_chrf_score({"pretranslations_chrf_score_avg": 0.0}) == 0.0


def test_get_chrf_score_rounded():
    """Score should be rounded to 2 decimal places."""
    assert get_chrf_score({"pretranslations_chrf_score_avg": 75.678}) == 75.68
