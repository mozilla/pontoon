import pytest

from pontoon.base.models import ChangedEntityLocale, Translation


@pytest.mark.django_db
def test_bulk_mark_changed_tolerates_concurrent_row(monkeypatch, translation_a):
    """A row created after the existing-rows read must not break the write."""
    ChangedEntityLocale.objects.get_or_create(
        entity=translation_a.entity, locale=translation_a.locale
    )
    # Simulate the read happening before the concurrent submission.
    monkeypatch.setattr(
        ChangedEntityLocale.objects,
        "values_list",
        lambda *args, **kwargs: ChangedEntityLocale.objects.none().values_list(
            *args, **kwargs
        ),
    )

    Translation.objects.filter(pk=translation_a.pk).bulk_mark_changed()

    assert (
        ChangedEntityLocale.objects.filter(
            entity=translation_a.entity, locale=translation_a.locale
        ).count()
        == 1
    )
