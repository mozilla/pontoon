
import types
from contextlib import nested

import pytest

from mock import MagicMock, patch, PropertyMock

from pontoon.tags.utils import TagsTool, TagTool


@pytest.mark.parametrize(
    "kwargs",
    [dict(tags_tool=None,
          name=None,
          pk=None,
          priority=None,
          project=None,
          slug=None),
     dict(tags_tool=1,
          name=2,
          pk=3,
          priority=4,
          project=5,
          slug=6,
          latest_translation=7,
          total_strings=8,
          approved_strings=9)])
def test_util_tag_tool_init(kwargs):
    tags_tool = TagTool(**kwargs)
    for k, v in kwargs.items():
        assert getattr(tags_tool, k) == v


@pytest.mark.django_db
def test_util_tag_tool_locale_stats(tag_matrix, tag_test_kwargs):
    name, kwargs = tag_test_kwargs
    tags_tool = TagsTool(**kwargs)
    if not len(tags_tool):
        assert "no_match" in name
        return
    tag_tool = list(tags_tool)[0]
    data = tag_tool.locale_stats
    # no dupes
    assert (
        len(set([(d['pk'], d['locale']) for d in data]))
        == len([(d['pk'], d['locale']) for d in data]))


@pytest.mark.django_db
def test_util_tag_tool_iter_locales():
    tag_tool = TagTool(
        TagsTool(),
        name=None,
        pk=None,
        priority=None,
        project=None,
        slug=None)
    _patch_ctx = nested(
        patch(
            'pontoon.tags.utils.tag.TagTool.locale_stats',
            new_callable=PropertyMock),
        patch(
            'pontoon.tags.utils.tag.TagTool.locale_latest',
            new_callable=PropertyMock),
        patch('pontoon.tags.utils.tag.TaggedLocale'))
    with _patch_ctx as (p_stats, p_latest, m_locale):
        m_locale.return_value = "X"
        _m_latest = MagicMock()
        _m_latest.get.return_value = 23
        p_latest.return_value = _m_latest
        p_stats.return_value = [
            dict(foo=1, locale=1),
            dict(foo=2, locale=2),
            dict(foo=3, locale=3)]
        locales = tag_tool.iter_locales()
        assert isinstance(locales, types.GeneratorType)
        result = list(locales)
        assert p_stats.called
        assert result == ['X'] * 3
        assert len(m_locale.call_args_list) == 3
        assert (
            list(list(a) for a in _m_latest.get.call_args_list)
            == [[(1,), {}], [(2,), {}], [(3,), {}]])
        for i, args in enumerate(m_locale.call_args_list):
            assert args[1]['foo'] == i + 1
            assert args[1]['latest_translation'] == 23


def test_util_tag_tool_linked_resources():
    tag_tool = TagTool(
        TagsTool(),
        name=None,
        pk=None,
        priority=None,
        project=None,
        slug=7)
    _patch_ctx = patch(
        'pontoon.tags.utils.TagTool.resource_tool',
        new_callable=PropertyMock)
    with _patch_ctx as p:
        resource_m = MagicMock()
        resource_m.get_linked_resources.return_value = 23
        p.return_value = resource_m
        linked = tag_tool.linked_resources
        assert linked == 23
        assert (
            list(resource_m.get_linked_resources.call_args)
            == [(7,), {}])


def test_util_tag_tool_linkable_resources():
    tag_tool = TagTool(
        TagsTool(),
        name=None,
        pk=None,
        priority=None,
        project=None,
        slug=7)
    _patch_ctx = patch(
        'pontoon.tags.utils.TagTool.resource_tool',
        new_callable=PropertyMock)
    with _patch_ctx as p:
        resource_m = MagicMock()
        resource_m.get_linkable_resources.return_value = 23
        p.return_value = resource_m
        linkable = tag_tool.linkable_resources
        assert linkable == 23
        assert (
            list(resource_m.get_linkable_resources.call_args)
            == [(7,), {}])


def test_util_tag_tool_link_resources():
    tag_tool = TagTool(
        TagsTool(),
        name=None,
        pk=None,
        priority=None,
        project=None,
        slug=7)
    _patch_ctx = patch(
        'pontoon.tags.utils.TagTool.resource_tool',
        new_callable=PropertyMock)
    with _patch_ctx as p:
        resource_m = MagicMock()
        resource_m.link.return_value = 23
        p.return_value = resource_m
        linkable = tag_tool.link_resources(13)
        assert linkable == 23
        assert (
            list(resource_m.link.call_args)
            == [(7,), {'resources': 13}])


def test_util_tag_tool_unlink_resources():
    tag_tool = TagTool(
        TagsTool(),
        name=None,
        pk=None,
        priority=None,
        project=None,
        slug=7)
    _patch_ctx = patch(
        'pontoon.tags.utils.TagTool.resource_tool',
        new_callable=PropertyMock)
    with _patch_ctx as p:
        resource_m = MagicMock()
        resource_m.unlink.return_value = 23
        p.return_value = resource_m
        unlinkable = tag_tool.unlink_resources(13)
        assert unlinkable == 23
        assert (
            list(resource_m.unlink.call_args)
            == [(7,), {'resources': 13}])


def test_util_tag_tool_object():
    _patch_ctx = patch(
        'pontoon.tags.utils.TagsTool.tag_manager',
        new_callable=PropertyMock)

    with _patch_ctx as manager_p:
        m_get = MagicMock()
        m_get.get.return_value = 23
        m_related = MagicMock()
        m_related.select_related.return_value = m_get
        manager_p.return_value = m_related
        tag_tool = TagTool(
            TagsTool(),
            name=None,
            pk=13,
            priority=None,
            project=None,
            slug=7)
        obj = tag_tool.object
        assert obj is 23
        assert (
            list(m_get.get.call_args)
            == [(), {'pk': 13}])


@pytest.mark.django_db
def test_util_tag_tool_url(locale0, project0):
    tag_tool = TagTool(
        TagsTool(),
        name=None,
        pk=13,
        priority=None,
        project=None,
        slug=7)
    _patch_ctx = patch(
        'pontoon.tags.utils.tag.reverse')
    with _patch_ctx as m:
        m.return_value = 23
        url = tag_tool.url()
        assert url == ''
        assert not m.called
        url = tag_tool.url(locale=locale0)
        assert url == ''
        assert not m.called
        url = tag_tool.url(project=project0)
        assert url == 23
        assert(
            list(m.call_args)
            == [('pontoon.tags.project.tag', ),
                {'kwargs': {
                    'tag': 7,
                    'project': project0.slug}}])
        m.reset_mock()
        url = tag_tool.url(project=project0, locale=locale0)
        assert url == 23
        assert(
            list(m.call_args)
            == [('pontoon.localizations.tags.tag', ),
                {'kwargs': {
                    'tag': 7,
                    'slug': project0.slug,
                    'code': locale0.code}}])
