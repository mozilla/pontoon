"""
Test consistency of calculations between `calculate_stats` and `translation.save()`.
"""

import pytest

from pontoon.base.models import TranslatedResource


def get_stats(translation):
    return TranslatedResource.objects.filter(
        resource=translation.entity.resource,
        locale=translation.locale,
    ).aggregated_stats()


@pytest.mark.django_db
def test_translation_approved(translation_a):
    translation_a.approved = True
    translation_a.save()

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 1,
        "pretranslated": 0,
        "unreviewed": 0,
        "warnings": 0,
        "errors": 0,
    }

    translation_a.approved = False
    translation_a.save()

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 0,
        "pretranslated": 0,
        "unreviewed": 1,
        "warnings": 0,
        "errors": 0,
    }


@pytest.mark.django_db
def test_translation_pretranslated(translation_a):
    translation_a.pretranslated = True
    translation_a.save()

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 0,
        "pretranslated": 1,
        "unreviewed": 0,
        "warnings": 0,
        "errors": 0,
    }

    translation_a.pretranslated = False
    translation_a.rejected = True
    translation_a.save()

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 0,
        "pretranslated": 0,
        "unreviewed": 0,
        "warnings": 0,
        "errors": 0,
    }


@pytest.mark.django_db
def test_translation_with_error(translation_a):
    translation_a.approved = True
    translation_a.save(failed_checks={"pErrors": ["error"]})

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 0,
        "pretranslated": 0,
        "unreviewed": 0,
        "warnings": 0,
        "errors": 1,
    }

    translation_a.approved = False
    translation_a.pretranslated = True
    translation_a.save()

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 0,
        "pretranslated": 0,
        "unreviewed": 0,
        "warnings": 0,
        "errors": 1,
    }

    translation_a.pretranslated = False
    translation_a.save()

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 0,
        "pretranslated": 0,
        "unreviewed": 1,
        "warnings": 0,
        "errors": 0,
    }


@pytest.mark.django_db
def test_translation_with_warning(translation_a):
    translation_a.approved = True
    translation_a.save(failed_checks={"pWarnings": ["warning"]})

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 0,
        "pretranslated": 0,
        "unreviewed": 0,
        "warnings": 1,
        "errors": 0,
    }

    translation_a.approved = False
    translation_a.pretranslated = True
    translation_a.save()

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 0,
        "pretranslated": 0,
        "unreviewed": 0,
        "warnings": 1,
        "errors": 0,
    }

    translation_a.pretranslated = False
    translation_a.save()

    assert get_stats(translation_a) == {
        "total": 1,
        "approved": 0,
        "pretranslated": 0,
        "unreviewed": 1,
        "warnings": 0,
        "errors": 0,
    }
