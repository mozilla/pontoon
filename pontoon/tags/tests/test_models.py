import pytest

from pontoon.tags.models import Tag
from pontoon.test.factories import TagFactory


@pytest.mark.django_db
def test_serialize_tags():
    # tests serialization of a QuerySet of Tags
    tag1 = TagFactory.create()
    tag2 = TagFactory.create()
    tag3 = TagFactory.create()

    pks = [tag1.pk, tag2.pk, tag3.pk]
    queryset = Tag.objects.filter(pk__in=pks)

    expected = [
        {"slug": tag1.slug, "name": tag1.name, "priority": tag1.priority},
        {"slug": tag2.slug, "name": tag2.name, "priority": tag2.priority},
        {"slug": tag3.slug, "name": tag3.name, "priority": tag3.priority},
    ]

    assert queryset.serialize() == expected
