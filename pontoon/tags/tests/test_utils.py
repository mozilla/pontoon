import pytest

from pontoon.tags.utils import Tags


@pytest.mark.django_db
def test_tags_get_no_project():
    tags = Tags().get()
    assert len(tags) == 0


@pytest.mark.django_db
def test_tags_get(project_a, tag_a, translation_a):
    tags = Tags(project=project_a).get()
    tag = tags[0]

    assert tag.name == tag_a.name
    assert tag.slug == tag_a.slug
    assert tag.priority == tag_a.priority
    assert tag.latest_activity == translation_a.latest_activity

    assert tag.chart == {
        "total": 1,
        "approved": 0,
        "pretranslated": 0,
        "errors": 0,
        "warnings": 0,
        "unreviewed": 1,
        "resource__tag": tag.id,
    }


@pytest.mark.django_db
def test_tags_get_tag_locales(project_a, project_locale_a, tag_a):
    tags = Tags(project=project_a, slug=tag_a.slug)
    tag = tags.get_tag_locales()

    assert tag.name == tag_a.name
    assert tag.priority == tag_a.priority
    assert tag.locales.count() == project_a.locales.all().count()
    assert tag.locales.first() == project_a.locales.all().first()

    with pytest.raises(AttributeError):
        tag.latest_activity

    assert tag.chart == {
        "total": 1,
        "approved": 0,
        "pretranslated": 0,
        "errors": 0,
        "warnings": 0,
        "unreviewed": 0,
        "resource__tag": tag.id,
    }

    locale = tag.locales.first()
    assert locale.latest_activity is None
    assert locale.chart == {
        "total": 1,
        "approved": 0,
        "pretranslated": 0,
        "errors": 0,
        "warnings": 0,
        "unreviewed": 0,
        "locale": locale.id,
    }
