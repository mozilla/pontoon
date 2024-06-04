from pontoon.tags.admin import TagsTool, TagTool
from unittest.mock import MagicMock, PropertyMock, patch


@patch("pontoon.tags.admin.TagTool.resource_tool", new_callable=PropertyMock)
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


@patch("pontoon.tags.admin.TagTool.resource_tool", new_callable=PropertyMock)
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


@patch("pontoon.tags.admin.TagTool.resource_tool", new_callable=PropertyMock)
def test_util_tag_tool_link_resources(resources_mock):
    tag_tool = TagTool(
        TagsTool(), name=None, pk=None, priority=None, project=None, slug=7
    )
    resources_mock.configure_mock(**{"return_value.link.return_value": 23})

    # link_resources returns resources.link()
    assert tag_tool.link_resources(13) == 23

    # resources.link() is called with correct args
    assert list(resources_mock.return_value.link.call_args) == [(7,), {"resources": 13}]


@patch("pontoon.tags.admin.TagTool.resource_tool", new_callable=PropertyMock)
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


@patch("pontoon.tags.admin.TagsTool.tag_manager", new_callable=PropertyMock)
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


@patch("pontoon.tags.admin.TagsTool.resource_tool", new_callable=PropertyMock)
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
