from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from pontoon.tags.models import Tag
from pontoon.tags.utils import (
    TagsLatestTranslationsTool,
    TagsResourcesTool,
    TagsStatsTool,
    TagsTool,
    TagTool,
)
from pontoon.tags.utils.base import Clonable


def test_util_tags_tool():
    # test tags tool instantiation
    tags_tool = TagsTool()
    assert tags_tool.tag_class is TagTool
    assert tags_tool.resources_class is TagsResourcesTool
    assert tags_tool.translations_class is TagsLatestTranslationsTool
    assert tags_tool.stats_class is TagsStatsTool
    assert tags_tool.locales is None
    assert tags_tool.projects is None
    assert tags_tool.priority is None
    assert tags_tool.slug is None
    assert tags_tool.path is None
    assert tags_tool.tag_manager == Tag.objects


@patch("pontoon.tags.utils.TagsTool.stats_class")
def test_util_tags_tool_stats(stats_mock, tag_init_kwargs):
    # tests instantiation of tag.stats_tool with different args
    tags_tool = TagsTool(**tag_init_kwargs)
    stats_mock.return_value = 23
    assert tags_tool.stat_tool == 23
    assert stats_mock.call_args[1] == tag_init_kwargs


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(slug=None, locales=None, projects=None, path=None),
        dict(slug=1, locales=2, projects=3, path=4),
    ],
)
@patch("pontoon.tags.utils.TagsTool.resources_class")
def test_util_tags_tool_resources(resources_mock, kwargs):
    # tests instantiation of tag.resources_tool with different args
    tags_tool = TagsTool(**kwargs)
    resources_mock.return_value = 23
    assert tags_tool.resource_tool == 23
    assert resources_mock.call_args[1] == kwargs


@pytest.mark.parametrize(
    "kwargs",
    [dict(slug=None, locales=None, projects=None), dict(slug=1, locales=2, projects=3)],
)
@patch("pontoon.tags.utils.TagsTool.translations_class")
def test_util_tags_tool_translations(trans_mock, kwargs):
    # tests instantiation of tag.translations_tool with different args
    tags_tool = TagsTool(**kwargs)
    trans_mock.return_value = 23
    assert tags_tool.translation_tool == 23
    assert trans_mock.call_args[1] == kwargs


@patch("pontoon.tags.utils.TagsTool.tag_class")
@patch("pontoon.tags.utils.TagsTool.get_tags")
@patch("pontoon.tags.utils.TagsTool.__len__")
@patch("pontoon.tags.utils.TagsTool.__iter__")
def test_util_tags_tool_get(iter_mock, len_mock, tags_mock, class_mock):
    # tests getting a TagTool from TagsTool
    tags_tool = TagsTool()
    class_mock.return_value = 23
    len_mock.return_value = 7
    iter_mock.return_value = iter([3, 17, 73])

    # with no slug returns first result from iter(self)
    assert tags_tool.get() == 3
    assert not class_mock.called
    assert not tags_mock.called
    assert len_mock.called
    assert iter_mock.called
    len_mock.reset_mock()
    iter_mock.reset_mock()

    # calling with slug creates a TagTool instance
    # and doesnt call iter(self) at all
    assert tags_tool.get(113) == 23
    assert not len_mock.called
    assert not iter_mock.called
    assert list(class_mock.call_args) == [(tags_tool,), {}]
    assert list(tags_mock.call_args) == [(), {"slug": 113}]


def test_util_tags_tool_call_and_clone():
    # tests cloning a TagsTool
    tags_tool = TagsTool()
    cloned = tags_tool()
    assert cloned is not tags_tool
    assert isinstance(tags_tool, Clonable)
    assert isinstance(cloned, Clonable)


@patch("pontoon.tags.utils.TagsTool.__call__")
def test_util_tags_tool_getitem(call_mock):
    # test that calling __getitem__ calls __call__ with slug
    tags_tool = TagsTool()
    slugs = ["foo", "bar"]
    for slug in slugs:
        tags_tool[slug]
    assert call_mock.call_args_list[0][1] == dict(slug=slugs[0])
    assert call_mock.call_args_list[1][1] == dict(slug=slugs[1])


@patch("pontoon.tags.utils.TagsTool.iter_tags")
@patch("pontoon.tags.utils.TagsTool.stat_tool", new_callable=PropertyMock)
def test_util_tags_tool_iter(stats_mock, iter_mock):
    # tests that when you iter it calls iter_tags with
    # stats data
    tags_tool = TagsTool()
    stats_mock.configure_mock(**{"return_value.data": [7, 23]})
    iter_mock.return_value = iter([])
    assert list(tags_tool) == []
    assert stats_mock.called
    assert list(iter_mock.call_args) == [([7, 23],), {}]


@patch("pontoon.tags.utils.TagsTool.stat_tool", new_callable=PropertyMock)
def test_util_tags_tool_len(stats_mock):
    # tests that when you len() you get the len
    # of the stats data
    m_len = MagicMock()
    m_len.__len__.return_value = 23
    stats_mock.configure_mock(**{"return_value.data": m_len})
    tags_tool = TagsTool()
    assert len(tags_tool) == 23
    assert m_len.__len__.called


@patch("pontoon.tags.utils.TagsTool.translation_tool", new_callable=PropertyMock)
@patch("pontoon.tags.utils.TagsTool.tag_class")
def test_util_tags_tool_iter_tags(tag_mock, trans_mock):
    # tests that iter_tags calls instantiates a TagTool with
    # stat data and latest_translation data

    trans_mock.configure_mock(**{"return_value.data.get.return_value": 23})
    tags_tool = TagsTool()
    list(
        tags_tool.iter_tags(
            [
                dict(resource__tag=1, foo="bar"),
                dict(resource__tag=2, foo="bar"),
                dict(resource__tag=3, foo="bar"),
            ]
        )
    )

    # translation_tool.data.get() was called 3 times with tag pks
    assert [x[0][0] for x in trans_mock.return_value.data.get.call_args_list] == [
        1,
        2,
        3,
    ]

    # TagTool was called 3 times with the tags tool as arg
    assert [x[0][0] for x in tag_mock.call_args_list] == [tags_tool] * 3

    # and stat + translation data as kwargs
    assert [x[1] for x in tag_mock.call_args_list] == [
        {"resource__tag": 1, "latest_translation": 23, "foo": "bar"},
        {"resource__tag": 2, "latest_translation": 23, "foo": "bar"},
        {"resource__tag": 3, "latest_translation": 23, "foo": "bar"},
    ]


@patch("pontoon.tags.utils.TagsTool.tag_manager", new_callable=PropertyMock)
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
