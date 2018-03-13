
from contextlib import nested

import pytest

from mock import MagicMock, patch, PropertyMock

from pontoon.tags.models import Tag
from pontoon.tags.utils import (
    TagsLatestTranslationsTool, TagsResourcesTool, TagsStatsTool,
    TagsTool, TagTool)


def test_util_tags_tool():
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


def test_util_tags_tool_stats(tag_init_kwargs):
    kwargs = tag_init_kwargs
    tags_tool = TagsTool(**kwargs)

    with patch('pontoon.tags.utils.TagsTool.stats_class') as m:
        m.return_value = 23
        assert tags_tool.stat_tool == 23
        assert m.call_args[1] == kwargs


@pytest.mark.parametrize(
    "kwargs",
    [dict(
        slug=None,
        locales=None,
        projects=None,
        path=None),
     dict(
         slug=1,
         locales=2,
         projects=3,
         path=4)])
def test_util_tags_tool_resources(kwargs):
    tags_tool = TagsTool(**kwargs)

    _patch_ctx = nested(
        patch('pontoon.tags.utils.TagsTool.resources_class'),
        patch('pontoon.tags.utils.TagsTool.stats_class'))

    with _patch_ctx as (m_res, m_stats):
        m_stats.return_value = 7
        m_res.return_value = 23
        assert tags_tool.resource_tool == 23
        assert m_res.call_args[1] == kwargs


@pytest.mark.parametrize(
    "kwargs",
    [dict(
        slug=None,
        locales=None,
        projects=None),
     dict(
         slug=1,
         locales=2,
         projects=3)])
def test_util_tags_tool_translations(kwargs):
    tags_tool = TagsTool(**kwargs)
    with patch('pontoon.tags.utils.TagsTool.translations_class') as m:
        m.return_value = 23
        assert tags_tool.translation_tool == 23
        assert m.call_args[1] == kwargs


@pytest.mark.parametrize(
    "slug,name",
    [['foo', None],
     ['bar', 'Baz'],
     [1, 2]])
def test_util_tags_tool_create(slug, name):
    tags_tool = TagsTool()

    _patch_ctx = patch(
        'pontoon.tags.utils.TagsTool.tag_manager',
        new_callable=PropertyMock)

    with _patch_ctx as m:
        m_create = MagicMock()
        m_obj = MagicMock()
        m_create.create.return_value = m_obj
        m.return_value = m_create
        result = tags_tool.create(slug, name)
        assert m.called
        assert result.pk is m_obj.pk
        assert result.name is m_obj.name
        assert result.priority is m_obj.priority
        assert result.project is m_obj.project
        assert result.slug is m_obj.slug
        assert (
            m_create.create.call_args[1]
            == dict(
                slug=slug,
                project=None,
                name=name or slug.capitalize()))


@pytest.mark.parametrize(
    "slug",
    [None, 1, 2])
def test_util_tags_tool_delete(slug):
    tags_tool = TagsTool()

    _patch_ctx = patch(
        'pontoon.tags.utils.TagsTool.tag_manager',
        new_callable=PropertyMock)

    with _patch_ctx as m:
        m_delete = MagicMock()
        m_delete.delete.return_value = 23
        m_get = MagicMock()
        m_get.get.return_value = m_delete
        m.return_value = m_get
        tags_tool.delete(slug)
        assert m.called
        assert (
            m_get.get.call_args[1]
            == dict(slug=slug))


def test_util_tags_tool_get():
    tags_tool = TagsTool()

    _patch_ctx = [
        patch('pontoon.tags.utils.TagsTool.tag_class'),
        patch('pontoon.tags.utils.TagsTool.get_tags'),
        patch('pontoon.tags.utils.TagsTool.__len__'),
        patch('pontoon.tags.utils.TagsTool.__iter__')]

    with nested(*_patch_ctx) as (class_m, tags_m, len_m, iter_m):
        class_m.return_value = 23
        len_m.return_value = 7
        iter_m.return_value = iter([3, 17, 73])
        result = tags_tool.get()
        assert result == 3
        assert not class_m.called
        assert not tags_m.called
        assert len_m.called
        assert iter_m.called
        len_m.reset_mock()
        iter_m.reset_mock()
        result = tags_tool.get(113)
        assert result == 23
        assert not len_m.called
        assert not iter_m.called
        assert (
            list(class_m.call_args)
            == [(tags_tool, ), {}])
        assert (
            list(tags_m.call_args)
            == [(), {'slug': 113}])


def test_util_tags_tool_call_and_clone(tag_init_kwargs):
    kwargs = tag_init_kwargs
    tags_tool = TagsTool(**kwargs)
    cloned = tags_tool()
    assert cloned is not tags_tool
    assert isinstance(cloned, TagsTool)
    for k, v in kwargs.items():
        assert getattr(tags_tool, k) == getattr(cloned, k)
    for k, v in kwargs.items():
        _cloned = cloned(**{k: 23})
        for _k, _v in kwargs.items():
            if k == _k:
                assert getattr(_cloned, _k) == 23
                assert getattr(tags_tool, _k) != getattr(_cloned, _k)
            else:
                assert getattr(tags_tool, _k) == getattr(_cloned, _k)


def test_util_tags_tool_getitem():
    tags_tool = TagsTool()
    slugs = ["foo", "bar"]
    for slug in slugs:
        with patch('pontoon.tags.utils.TagsTool.__call__') as m:
            tags_tool[slug]
            assert m.call_args[1] == dict(slug=slug)


def test_util_tags_tool_iter():
    tags_tool = TagsTool()

    _patch_ctx = nested(
        patch('pontoon.tags.utils.TagsTool.iter_tags'),
        patch('pontoon.tags.utils.TagsTool.stat_tool',
              new_callable=PropertyMock))

    with _patch_ctx as (m_iter, m_stats):
        m_tags = MagicMock()
        type(m_tags).data = PropertyMock(return_value=[7, 23])
        m_stats.return_value = m_tags
        m_iter.return_value = iter([])
        assert list(tags_tool) == []
        assert m_stats.called
        assert (
            list(m_iter.call_args)
            == [([7, 23],), {}])


def test_util_tags_tool_len():
    _patch_ctx = patch(
        'pontoon.tags.utils.TagsTool.stat_tool',
        new_callable=PropertyMock)

    with _patch_ctx as p:
        m_len = MagicMock()
        m_len.__len__.return_value = 23
        data_p = PropertyMock()
        type(data_p).data = PropertyMock(return_value=m_len)
        p.return_value = data_p
        tags_tool = TagsTool()
        assert len(tags_tool) == 23
        assert m_len.__len__.called


def test_util_tags_tool_iter_tags():
    tags_tool = TagsTool()

    _patch_ctx = nested(
        patch('pontoon.tags.utils.TagsTool.translation_tool',
              new_callable=PropertyMock),
        patch('pontoon.tags.utils.TagsTool.tag_class'))

    with _patch_ctx as (m_trans, m_tag):
        m_get = MagicMock()
        m_get.get.return_value = 23
        m_latest = MagicMock()
        _p = PropertyMock(return_value=m_get)
        type(m_latest).data = _p
        m_trans.return_value = m_latest
        list(
            tags_tool.iter_tags(
                [dict(resource__tag=1, foo="bar"),
                 dict(resource__tag=2, foo="bar"),
                 dict(resource__tag=3, foo="bar")]))
        assert (
            [x[0][0] for x in m_get.get.call_args_list]
            == [1, 2, 3])
        assert (
            [x[0][0] for x in m_tag.call_args_list]
            == [tags_tool] * 3)
        assert (
            [x[1] for x in m_tag.call_args_list]
            == [{'resource__tag': 1, 'latest_translation': 23, 'foo': 'bar'},
                {'resource__tag': 2, 'latest_translation': 23, 'foo': 'bar'},
                {'resource__tag': 3, 'latest_translation': 23, 'foo': 'bar'}])
