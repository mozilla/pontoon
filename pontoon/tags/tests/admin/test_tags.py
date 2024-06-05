from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from pontoon.tags.admin import (
    TagsResourcesTool,
    TagsTool,
    TagTool,
)
from pontoon.tags.admin.base import Clonable
from pontoon.tags.models import Tag


def test_util_tags_tool():
    # test tags tool instantiation
    tags_tool = TagsTool()
    assert tags_tool.tag_class is TagTool
    assert tags_tool.resources_class is TagsResourcesTool
    assert tags_tool.locales is None
    assert tags_tool.projects is None
    assert tags_tool.priority is None
    assert tags_tool.slug is None
    assert tags_tool.path is None
    assert tags_tool.tag_manager == Tag.objects


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(slug=None, locales=None, projects=None, path=None),
        dict(slug=1, locales=2, projects=3, path=4),
    ],
)
@patch("pontoon.tags.admin.TagsTool.resources_class")
def test_util_tags_tool_resources(resources_mock, kwargs):
    # tests instantiation of tag.resources_tool with different args
    tags_tool = TagsTool(**kwargs)
    resources_mock.return_value = 23
    assert tags_tool.resource_tool == 23
    assert resources_mock.call_args[1] == kwargs


@patch("pontoon.tags.admin.TagsTool.tag_class")
@patch("pontoon.tags.admin.TagsTool.get_tags")
def test_util_tags_tool_get(tags_mock, class_mock):
    # tests getting a TagTool from TagsTool
    tags_tool = TagsTool()
    class_mock.return_value = 23

    # calling with slug creates a TagTool instance
    assert tags_tool.get(113) == 23
    assert list(class_mock.call_args) == [(tags_tool,), {}]
    assert list(tags_mock.call_args) == [(), {"slug": 113}]


def test_util_tags_tool_call_and_clone():
    # tests cloning a TagsTool
    tags_tool = TagsTool()
    cloned = tags_tool()
    assert cloned is not tags_tool
    assert isinstance(tags_tool, Clonable)
    assert isinstance(cloned, Clonable)


@patch("pontoon.tags.admin.TagsTool.__call__")
def test_util_tags_tool_getitem(call_mock):
    # test that calling __getitem__ calls __call__ with slug
    tags_tool = TagsTool()
    slugs = ["foo", "bar"]
    for slug in slugs:
        tags_tool[slug]
    assert call_mock.call_args_list[0][1] == dict(slug=slugs[0])
    assert call_mock.call_args_list[1][1] == dict(slug=slugs[1])


@patch("pontoon.tags.admin.TagsTool.tag_manager", new_callable=PropertyMock)
def test_util_tags_tool_get_tags(tag_mock):
    filter_mock = MagicMock(**{"filter.return_value": 23})
    tag_mock.configure_mock(
        **{"return_value.filter.return_value.values.return_value": filter_mock}
    )
    tags_tool = TagsTool()

    # no slug provided, returns `values`
    assert tags_tool.get_tags() is filter_mock
    assert not filter_mock.called
    assert list(tag_mock.return_value.filter.return_value.values.call_args) == [
        ("pk", "name", "slug", "priority", "project"),
        {},
    ]

    tag_mock.reset_mock()

    # slug provided, `values` is filtered
    assert tags_tool.get_tags("FOO") == 23
    assert list(filter_mock.filter.call_args) == [(), {"slug": "FOO"}]
    assert list(tag_mock.return_value.filter.return_value.values.call_args) == [
        ("pk", "name", "slug", "priority", "project"),
        {},
    ]
