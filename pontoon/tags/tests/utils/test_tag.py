import types
from unittest.mock import patch, MagicMock, PropertyMock

import pytest

from pontoon.tags.utils import TagsTool, TagTool


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(
            tags_tool=None, name=None, pk=None, priority=None, project=None, slug=None
        ),
        dict(
            tags_tool=1,
            name=2,
            pk=3,
            priority=4,
            project=5,
            slug=6,
            latest_translation=7,
            total_strings=8,
            approved_strings=9,
        ),
    ],
)
def test_util_tag_tool_init(kwargs):
    # Test the TagTool can be instantiated with/out args
    tags_tool = TagTool(**kwargs)
    for k, v in kwargs.items():
        assert getattr(tags_tool, k) == v


@patch("pontoon.tags.utils.tags.TagsTool.stat_tool", new_callable=PropertyMock())
def test_util_tag_tool_locale_stats(stats_mock):
    stats_mock.configure_mock(**{"return_value.data": 23})
    tag_tool = TagTool(
        TagsTool(), name=None, pk=None, priority=None, project=None, slug=7
    )

    # locale_stats returns self.tags_tool.stats_tool().data
    assert tag_tool.locale_stats == 23

    # stats_tool was called with slug and groupby
    assert list(stats_mock.call_args) == [(), {"groupby": "locale", "slug": 7}]


@patch("pontoon.tags.utils.tag.TagTool.locale_stats", new_callable=PropertyMock)
@patch("pontoon.tags.utils.tag.TagTool.locale_latest", new_callable=PropertyMock)
@patch("pontoon.tags.utils.tag.TaggedLocale")
def test_util_tag_tool_iter_locales(locale_mock, latest_mock, stats_mock):
    tag_tool = TagTool(
        TagsTool(), name=None, pk=None, priority=None, project=None, slug=None
    )

    # Set mocks
    locale_mock.return_value = "X"
    latest_mock.configure_mock(**{"return_value.get.return_value": 23})
    stats_mock.return_value = [
        dict(foo=1, locale=1),
        dict(foo=2, locale=2),
        dict(foo=3, locale=3),
    ]

    # iter_locales - should generate 3 of 'X'
    locales = tag_tool.iter_locales()
    assert isinstance(locales, types.GeneratorType)
    assert list(locales) == ["X"] * 3
    assert len(locale_mock.call_args_list) == 3
    assert stats_mock.called

    # locale_latest is called with each of the locales
    assert list(list(a) for a in latest_mock.return_value.get.call_args_list) == [
        [(1,), {}],
        [(2,), {}],
        [(3,), {}],
    ]

    # TaggedLocale is called with locale data
    for i, args in enumerate(locale_mock.call_args_list):
        assert args[1]["foo"] == i + 1
        assert args[1]["latest_translation"] == 23


@patch("pontoon.tags.utils.TagTool.resource_tool", new_callable=PropertyMock)
def test_util_tag_tool_linked_resources(resources_mock):
    tag_tool = TagTool(
        TagsTool(), name=None, pk=None, priority=None, project=None, slug=7
    )
    resources_mock.configure_mock(
        **{
            "return_value.get_linked_resources"
            ".return_value.order_by.return_value": 23
        }
    )

    # linked_resources returns
    # resources.get_linked_resources().order_by()
    assert tag_tool.linked_resources == 23

    # get_linked_resources was called with slug
    linked_resources_mock = resources_mock.return_value.get_linked_resources
    assert list(linked_resources_mock.call_args) == [(7,), {}]

    # order_by is called with 'path'
    order_by_mock = linked_resources_mock.return_value.order_by
    assert list(order_by_mock.call_args) == [("path",), {}]


@patch("pontoon.tags.utils.TagTool.resource_tool", new_callable=PropertyMock)
def test_util_tag_tool_linkable_resources(resources_mock):
    tag_tool = TagTool(
        TagsTool(), name=None, pk=None, priority=None, project=None, slug=7
    )
    resources_mock.configure_mock(
        **{
            "return_value.get_linkable_resources"
            ".return_value.order_by.return_value": 23
        }
    )

    # linkable_resources returns
    # resources.get_linkable_resources().order_by()
    assert tag_tool.linkable_resources == 23

    # get_linkable_resources was called with slug
    linkable_resources_mock = resources_mock.return_value.get_linkable_resources
    assert list(linkable_resources_mock.call_args) == [(7,), {}]

    # order_by is called with 'path'
    order_by_mock = linkable_resources_mock.return_value.order_by
    assert list(order_by_mock.call_args) == [("path",), {}]


@patch("pontoon.tags.utils.TagTool.resource_tool", new_callable=PropertyMock)
def test_util_tag_tool_link_resources(resources_mock):
    tag_tool = TagTool(
        TagsTool(), name=None, pk=None, priority=None, project=None, slug=7
    )
    resources_mock.configure_mock(**{"return_value.link.return_value": 23})

    # link_resources returns resources.link()
    assert tag_tool.link_resources(13) == 23

    # resources.link() is called with correct args
    assert list(resources_mock.return_value.link.call_args) == [(7,), {"resources": 13}]


@patch("pontoon.tags.utils.TagTool.resource_tool", new_callable=PropertyMock)
def test_util_tag_tool_unlink_resources(resources_mock):
    tag_tool = TagTool(
        TagsTool(), name=None, pk=None, priority=None, project=None, slug=7
    )
    resources_mock.configure_mock(**{"return_value.unlink.return_value": 23})

    # unlink_resources returns resources.unlink()
    assert tag_tool.unlink_resources(13) == 23

    # resources.unlink() is called with correct args
    assert list(resources_mock.return_value.unlink.call_args) == [
        (7,),
        {"resources": 13},
    ]


@patch("pontoon.tags.utils.TagsTool.tag_manager", new_callable=PropertyMock)
def test_util_tag_tool_object(tag_mock):
    tag_mock.configure_mock(
        **{"return_value.select_related" ".return_value.get.return_value": 23}
    )
    tag_tool = TagTool(
        TagsTool(), name=None, pk=13, priority=None, project=None, slug=7
    )

    # object returns tag_manager.select_related().get()
    assert tag_tool.object == 23

    # tag_manager.select_related().get() is called with the tag pk
    assert list(tag_mock.return_value.select_related.return_value.get.call_args) == [
        (),
        {"pk": 13},
    ]


@patch("pontoon.tags.utils.TagsTool.resource_tool", new_callable=PropertyMock)
def test_util_tag_tool_resource_tool(resources_mock):
    tool_mock = MagicMock(return_value=23)
    resources_mock.return_value = tool_mock
    tag_tool = TagTool(
        TagsTool(), name=None, pk=None, priority=None, project=None, slug=None
    )

    # no project set - returns the tags.resources_tool, but doesnt call it
    assert tag_tool.resource_tool is tool_mock
    assert not tool_mock.called

    # project set
    tag_tool = TagTool(
        TagsTool(), name=None, pk=None, priority=None, project=43, slug=None
    )
    # tool was called with project as args
    assert tag_tool.resource_tool == 23
    assert list(tool_mock.call_args) == [(), {"projects": [43]}]


@patch("pontoon.tags.utils.TagsTool.translation_tool")
def test_util_tag_tool_locale_latest(trans_mock):
    trans_mock.configure_mock(**{"return_value.data": 23})
    tag_tool = TagTool(
        TagsTool(), name=None, pk=None, priority=None, project=None, slug=17
    )
    assert tag_tool.locale_latest == 23
    assert list(trans_mock.call_args) == [(), {"groupby": "locale", "slug": 17}]
