import pytest

from pontoon.base.models import (
    Locale,
    Project,
    Resource,
    TranslatedResource,
    Translation,
)

from pontoon.tags.models import Tag
from pontoon.tags.utils.base import Clonable, TagsDataTool


def test_util_clonable():
    # tests that Clonable clones

    class MockClonable(Clonable):
        clone_kwargs = ("foo", "bar")

    clonable = MockClonable()
    assert clonable.foo is None
    assert clonable.bar is None
    assert clonable().foo is None
    assert clonable().bar is None
    assert clonable(foo=7).foo == 7
    assert clonable(bar=23).bar == 23

    clonable = MockClonable(foo=7)
    assert clonable.foo == 7
    assert clonable.bar is None
    assert clonable().foo == 7
    assert clonable().bar is None
    assert clonable(foo=113).foo == 113
    assert clonable(foo=113).bar is None
    assert clonable(bar=23).bar == 23


def test_util_tags_data_tool_managers():
    # tests that the data tool has expected managers

    tool = TagsDataTool()
    assert tool.tag_manager == Tag.objects
    assert tool.locale_manager == Locale.objects
    assert tool.project_manager == Project.objects
    assert tool.resource_manager == Resource.objects
    assert tool.tr_manager == TranslatedResource.objects
    assert tool.translation_manager == Translation.objects


def test_util_tags_data_tool_instance():
    # tests that base tool does not implement a data_manager
    # and that the default coalesce is to return the data

    tool = TagsDataTool()

    with pytest.raises(NotImplementedError):
        tool.data_manager

    assert tool.coalesce("X") == "X"
