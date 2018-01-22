
import fnmatch
import types
from contextlib import nested

import pytest

from mock import MagicMock, patch, PropertyMock

from django.db.models import F, QuerySet

from pontoon.base.models import (
    Resource, TranslatedResource, Translation)
from pontoon.tags.models import Tag
from pontoon.tags.utils import (
    TagChart, Tagged, TaggedResource, TaggedProject, TagsResourcesTool,
    TagsStatsTool, TagsTool, TagsTranslationsTool, TagTool)


@pytest.mark.parametrize(
    "inputs, outputs",
    [[(2, 3, 4, 5), (40, 40.0, 60.0, 80.0)],
     [(7, 23, 43, 100), (7, 7.0, 23.0, 43.0)],
     [(6, 13, 43, 73), (8, 8.0, 18.0, 59.0)],
     [(0, 0, 7, 11), (0, 0.0, 0.0, 64.0)]])
def test_util_tag_chart(inputs, outputs):
    chart = TagChart(
        approved_strings=inputs[0],
        fuzzy_strings=inputs[1],
        translated_strings=inputs[2],
        total_strings=inputs[3])
    assert chart.approved_strings == inputs[0]
    assert chart.fuzzy_strings == inputs[1]
    assert chart.translated_strings == inputs[2]
    assert chart.total_strings == inputs[3]

    assert chart.approved_percent == outputs[0]
    assert chart.approved_share == outputs[1]
    assert chart.fuzzy_share == outputs[2]
    assert chart.translated_share == outputs[3]


def test_util_tag_tagged():
    tagged = Tagged()
    assert tagged.latest_activity is None
    with patch('pontoon.tags.utils.TagChart') as m:
        assert tagged.chart is None
        assert not m.called
    assert tagged.kwargs == {}

    tagged = Tagged(foo='bar')
    assert tagged.latest_activity is None
    with patch('pontoon.tags.utils.TagChart') as m:
        assert tagged.chart is None
        assert not m.called
    assert tagged.kwargs == dict(foo='bar')

    tagged = Tagged(total_strings=23)
    assert tagged.latest_activity is None
    with patch('pontoon.tags.utils.TagChart') as m:
        m.return_value = "x"
        assert tagged.chart == "x"
        assert m.call_args[1]['total_strings'] == 23
    assert tagged.kwargs == dict(total_strings=23)

    m_latest = MagicMock()
    _p = PropertyMock(return_value="y")
    type(m_latest).latest_activity = _p
    tagged = Tagged(latest_translation=m_latest)
    assert tagged.latest_activity == "y"
    assert _p.called
    with patch('pontoon.tags.utils.TagChart') as m:
        assert tagged.chart is None
        assert not m.called
    assert tagged.kwargs == {}


def test_util_tag_tagged_resource():
    tagged = TaggedResource()
    assert tagged.path is None
    assert tagged.title is None
    assert tagged.project is None
    assert tagged.latest_activity is None
    assert tagged.kwargs == {}

    tagged = TaggedResource(path="foo")
    assert tagged.path == "foo"
    assert tagged.title == "foo"
    assert tagged.project is None
    assert tagged.latest_activity is None
    assert tagged.kwargs == dict(path="foo")

    tagged = TaggedResource(project="bar")
    assert tagged.path is None
    assert tagged.title is None
    assert tagged.project == "bar"
    assert tagged.latest_activity is None
    assert tagged.kwargs == dict(project="bar")

    m_latest = MagicMock()
    _p = PropertyMock(return_value="y")
    type(m_latest).latest_activity = _p
    tagged = TaggedResource(latest_translation=m_latest, total_strings=23)
    assert tagged.latest_activity == "y"
    assert _p.called
    with patch('pontoon.tags.utils.TagChart') as m:
        m.return_value = "x"
        assert tagged.chart == "x"
        assert m.call_args[1]['total_strings'] == 23


def test_util_tag_tagged_project():
    tagged = TaggedProject()
    assert tagged.slug is None
    assert tagged.name is None
    assert tagged.deadline is None
    assert tagged.priority is None
    assert tagged.total_strings is None
    assert tagged.latest_activity is None
    assert tagged.kwargs == {}

    tagged = TaggedProject(
        project=23,
        project_slug="foo",
        project_name="A foo")
    assert tagged.slug == "foo"
    assert tagged.name == "A foo"
    assert tagged.deadline is None
    assert tagged.priority is None
    assert tagged.total_strings is None
    assert tagged.latest_activity is None
    assert (
        tagged.kwargs
        == dict(
            project=23,
            project_slug="foo",
            project_name="A foo"))

    tagged = TaggedProject(
        project_deadline="foo",
        project_priority=23)
    assert tagged.slug is None
    assert tagged.name is None
    assert tagged.deadline == "foo"
    assert tagged.priority == 23
    assert tagged.total_strings is None
    assert tagged.latest_activity is None
    assert (
        tagged.kwargs
        == dict(project_deadline="foo", project_priority=23))

    m_latest = MagicMock()
    _p = PropertyMock(return_value="y")
    type(m_latest).latest_activity = _p
    tagged = TaggedProject(latest_translation=m_latest, total_strings=23)
    assert tagged.latest_activity == "y"
    assert _p.called
    with patch('pontoon.tags.utils.TagChart') as m:
        m.return_value = "x"
        assert tagged.chart == "x"
        assert m.call_args[1]['total_strings'] == 23


def test_util_tags_tool():
    tags_tool = TagsTool()
    assert tags_tool.tag_class is TagTool
    assert tags_tool.resources_class is TagsResourcesTool
    assert tags_tool.translations_class is TagsTranslationsTool
    assert tags_tool.stats_class is TagsStatsTool
    assert tags_tool.locales is None
    assert tags_tool.projects is None
    assert tags_tool.priority is None
    assert tags_tool.slug is None
    assert tags_tool.path is None
    assert tags_tool.groupby is None
    assert tags_tool.annotations is None
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
        m_stats.return_value = 23
        m_iter.return_value = iter([])
        list(tags_tool)
        assert m_stats.called
        assert m_iter.call_args[0][0] == m_stats.return_value


def test_util_tags_tool_len():
    tags_tool = TagsTool()

    _patch_ctx = patch(
        'pontoon.tags.utils.TagsTool.stat_tool',
        new_callable=PropertyMock)

    with _patch_ctx as m:
        m_len = MagicMock()
        m_len.__len__.return_value = 23
        m.return_value = m_len
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
        type(m_latest).latest = _p
        m_trans.return_value = m_latest
        list(
            tags_tool.iter_tags(
                [dict(pk=1, foo="bar"),
                 dict(pk=2, foo="bar"),
                 dict(pk=3, foo="bar")]))
        assert (
            [x[0][0] for x in m_get.get.call_args_list]
            == [1, 2, 3])
        assert (
            [x[0][0] for x in m_tag.call_args_list]
            == [tags_tool] * 3)
        assert (
            [x[1] for x in m_tag.call_args_list]
            == [{'pk': 1, 'latest_translation': 23, 'foo': 'bar'},
                {'pk': 2, 'latest_translation': 23, 'foo': 'bar'},
                {'pk': 3, 'latest_translation': 23, 'foo': 'bar'}])


def test_util_tags_stats_tool(tag_init_kwargs):
    kwargs = tag_init_kwargs
    stats_tool = TagsStatsTool(**kwargs)
    for k, v in kwargs.items():
        if k == "annotations":
            assert getattr(stats_tool, "_%s" % k) == (v or {})
        elif k == "groupby":
            assert getattr(stats_tool, "_%s" % k) == (v or [])
        else:
            assert getattr(stats_tool, k) == v


def test_util_tags_stats_tool_annotations():
    stats_tool = TagsStatsTool()
    assert stats_tool.annotations == stats_tool.default_annotations

    anno = dict(foo="foo0", bar="bar0")
    stats_tool = TagsStatsTool(annotations=anno)
    assert stats_tool.annotations != stats_tool.default_annotations
    assert stats_tool.annotations != anno
    anno.update(stats_tool.default_annotations)
    assert stats_tool.annotations == anno


def test_util_tags_stats_tool_groupby():
    stats_tool = TagsStatsTool()
    assert stats_tool.groupby == ["pk"]

    groupby = [1, 2, 3]
    stats_tool = TagsStatsTool(groupby=groupby)
    assert stats_tool.groupby != ["pk"]
    assert stats_tool.groupby != groupby
    assert stats_tool.groupby == ["pk"] + groupby


def test_util_tags_stats_tool_tr_manager():
    stats_tool = TagsStatsTool()
    assert stats_tool.tr_manager == TranslatedResource.objects


def test_util_tags_stats_tool_data():
    stats_tool = TagsStatsTool()
    _patch_ctx = patch(
        'pontoon.tags.utils.TagsStatsTool.get_data')
    with _patch_ctx as m:
        m.return_value = (1, 2, 3)
        result = stats_tool.data
        assert result == [1, 2, 3]
        assert m.called
        m.reset_mock()
        m.return_value = (4, 5, 6)
        result = stats_tool.data
        assert not m.called
        assert result == [1, 2, 3]
        del stats_tool.__dict__["data"]
        result = stats_tool.data
        assert m.called
        assert result == [4, 5, 6]


def test_util_tags_stats_tool_len():
    stats_tool = TagsStatsTool()
    _patch_ctx = patch(
        'pontoon.tags.utils.TagsStatsTool.data',
        new_callable=PropertyMock)
    with _patch_ctx as m:
        m.return_value = [7, 23]
        result = len(stats_tool)
        assert m.called
        assert result == 2


def test_util_tags_stats_tool_iter():
    stats_tool = TagsStatsTool()
    _patch_ctx = patch(
        'pontoon.tags.utils.TagsStatsTool.data',
        new_callable=PropertyMock)
    with _patch_ctx as m:
        m.return_value = [7, 23]
        result = list(stats_tool)
        assert m.called
        assert result == [7, 23]


def test_util_tags_stats_tool_filters():
    stats_tool = TagsStatsTool()
    assert (
        stats_tool.filters
        == [getattr(stats_tool, "filter_%s" % f)
            for f
            in stats_tool._filters])


def test_util_tags_stats_tool_trs():
    stats_tool = TagsStatsTool()
    _patch_ctx = nested(
        patch('pontoon.tags.utils.TagsStatsTool.tr_manager',
              new_callable=PropertyMock),
        patch('pontoon.tags.utils.TagsStatsTool.filter_empty'),
        patch('pontoon.tags.utils.TagsStatsTool.filter_locales'),
        patch('pontoon.tags.utils.TagsStatsTool.filter_projects'),
        patch('pontoon.tags.utils.TagsStatsTool.filter_priority'),
        patch('pontoon.tags.utils.TagsStatsTool.filter_slug'),
        patch('pontoon.tags.utils.TagsStatsTool.filter_path'))
    with _patch_ctx as m:
        m_trs, m_empty, m_locales, m_proj, m_prio, m_slug, m_path = m
        _m = MagicMock()
        _m.all.return_value = 0
        m_trs.return_value = _m
        for i, _m in enumerate(m[1:]):
            _m.return_value = i + 1
        result = stats_tool.trs
        assert result == i + 1
        for i, _m in enumerate(m):
            assert _m.called
            if i > 0:
                assert _m.call_args[0][0] == i - 1


def test_util_tags_stats_tool_tag_trs():
    stats_tool = TagsStatsTool()
    _patch_ctx = patch(
        'pontoon.tags.utils.TagsStatsTool.trs',
        new_callable=PropertyMock)
    with _patch_ctx as m:
        _m = MagicMock()
        _m.annotate.return_value = 23
        m.return_value = _m
        result = stats_tool.tag_trs
        assert result == 23
        annotation = _m.annotate.call_args[1]['pk']
        assert isinstance(annotation, F)
        assert annotation.name == 'resource__tag'


@pytest.mark.django_db
def test_util_tags_stats_tool_get_data_empty():
    stats_tool = TagsStatsTool()
    data = stats_tool.get_data()
    assert isinstance(data, QuerySet)
    assert list(data) == []


@pytest.mark.django_db
def test_util_tags_stats_tool_get_data(calculate_tags, assert_tags):
    stats_tool = TagsStatsTool()
    data = stats_tool.get_data()
    assert isinstance(data, QuerySet)
    assert_tags(
        calculate_tags(),
        data)


@pytest.mark.django_db
def test_util_tags_stats_tool_get_data_matrix(tag_matrix, calculate_tags,
                                              assert_tags, tag_test_kwargs):
    name, kwargs = tag_test_kwargs
    stats_tool = TagsStatsTool(**kwargs)
    data = stats_tool.get_data()
    assert isinstance(data, QuerySet)
    assert_tags(calculate_tags(**kwargs), data)
    if "exact" in name:
        assert len(data) == 1
    if "glob" in name:
        assert len(data) > 1
        assert len(data) < len(tag_matrix['tags'])
    if "no_match" in name:
        assert len(data) == 0
    elif "match" in name:
        assert len(data) > 0
    if kwargs.get("slug"):
        for result in data:
            assert fnmatch.fnmatch(result['slug'], kwargs["slug"])


@pytest.mark.parametrize(
    "kwargs",
    [dict(),
     dict(projects=1, path=2)])
def test_util_tags_resources_tool_params(kwargs):
    resource_tool = TagsResourcesTool(**kwargs)
    for k in ['projects', 'path']:
        assert getattr(resource_tool, k) == kwargs.get(k)
    assert resource_tool.tag_manager == Tag.objects
    assert resource_tool.resource_manager == Resource.objects


@pytest.mark.django_db
def test_util_tags_resources_tool_find(tag0, tag1):
    resource_tool = TagsResourcesTool()

    data = resource_tool.find('*')
    assert isinstance(data, QuerySet)
    assert data.count() == Resource.objects.count()

    resource0 = tag0.resources.first()
    data = resource_tool.find(resource0.path)
    assert isinstance(data, QuerySet)
    assert data.count() == 1
    assert data[0] == resource0

    data = resource_tool.find('*', exclude=tag0.slug)
    assert isinstance(data, QuerySet)
    assert data.count()
    assert resource0 not in data

    data = resource_tool.find('*', include=tag0.slug)
    assert isinstance(data, QuerySet)
    assert data.count() == 1
    assert resource0 in data

    resource_tool = TagsResourcesTool(projects=[resource0.project])
    data = resource_tool.find('*')
    assert (
        data.count()
        == Resource.objects.filter(project=resource0.project).count())
    assert data[0].project == resource0.project


@pytest.mark.django_db
def test_util_tags_resources_tool_add(resource0, tagX):
    resource_tool = TagsResourcesTool()

    assert tagX.resources.count() == 0
    resource_tool.add(tagX.slug, '*')
    assert tagX.resources.count() == Resource.objects.count()

    tagX.resources.remove(*list(tagX.resources.all()))
    resource_tool.add(tagX.slug, resource0.path)
    assert tagX.resources.count() == 1
    assert resource0 in tagX.resources.all()


@pytest.mark.django_db
def test_util_tags_resources_tool_remove(tag0, resourceX):
    resource0 = tag0.resources.first()
    resource_tool = TagsResourcesTool()

    tag0.resources.add(resourceX)
    assert tag0.resources.count() == 2
    resource_tool.remove(tag0.slug, '*')
    assert tag0.resources.count() == 0

    tag0.resources.add(resource0, resourceX)
    resource_tool.remove(tag0.slug, resource0.path)
    assert tag0.resources.count() == 1
    assert resourceX in tag0.resources.all()


def test_util_tags_translations_tool():
    tr_tool = TagsTranslationsTool()
    assert tr_tool.locales is None
    assert tr_tool.projects is None
    assert tr_tool.slug is None
    assert tr_tool.translation_manager == Translation.objects
    assert tr_tool.tr_manager == TranslatedResource.objects


@pytest.mark.django_db
def test_util_tags_translation_tool_get_last_changes(tag_matrix,
                                                     calculate_tags_latest,
                                                     tag_test_kwargs):
    name, kwargs = tag_test_kwargs
    exp = calculate_tags_latest(**kwargs)
    tr_tool = TagsTranslationsTool(**kwargs)
    data = tr_tool.get_latest()
    for k, (pk, date) in exp.items():
        assert data[k].date == date
        assert data[k].pk == pk
    if "exact" in name:
        assert len(data) == 1
    if "glob" in name:
        assert len(data) > 1
        assert len(data) < len(tag_matrix['tags'])
    if "no_match" in name:
        assert len(data) == 0
    elif "match" in name:
        assert len(data) > 0


def test_util_tags_translation_tool_last_change():
    tr_tool = TagsTranslationsTool()
    _patch_ctx = patch(
        'pontoon.tags.utils.TagsTranslationsTool.get_last_changes')
    with _patch_ctx as m:
        m.return_value = (1, 2, 3)
        result = tr_tool.last_changes
        assert result == [1, 2, 3]
        assert m.called
        m.reset_mock()
        m.return_value = (4, 5, 6)
        result = tr_tool.last_changes
        assert not m.called
        assert result == [1, 2, 3]
        del tr_tool.__dict__["last_changes"]
        result = tr_tool.last_changes
        assert m.called
        assert result == [4, 5, 6]


def test_util_tags_translation_tool_latest():
    tr_tool = TagsTranslationsTool()
    _patch_ctx = patch(
        'pontoon.tags.utils.TagsTranslationsTool.get_latest')
    with _patch_ctx as m:
        m.return_value = (1, 2, 3)
        result = tr_tool.latest
        assert result == (1, 2, 3)
        assert m.called
        m.reset_mock()
        m.return_value = (4, 5, 6)
        result = tr_tool.latest
        assert not m.called
        assert result == (1, 2, 3)
        del tr_tool.__dict__["latest"]
        result = tr_tool.latest
        assert m.called
        assert result == (4, 5, 6)


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
def test_util_tag_tool_resources(tag_test_kwargs):
    name, kwargs = tag_test_kwargs
    tags_tool = TagsTool(**kwargs)
    for tag_tool in tags_tool:
        tag = Tag.objects.get(pk=tag_tool.pk)
        assert isinstance(tag_tool.resources, QuerySet)
        expected = tag.resources.all()
        if kwargs.get("projects"):
            expected = expected.filter(
                project__in=kwargs["projects"])
        if kwargs.get("locales"):
            expected = expected.filter(
                translatedresources__locale__in=kwargs["locales"]).distinct()
        if kwargs.get("path"):
            _expected = list(
                t for t
                in expected.order_by('pk')
                if fnmatch.fnmatch(t.path, kwargs["path"]))
        else:
            _expected = list(expected.order_by('pk'))
        _tags = list(tag_tool.resources.order_by('pk'))
        assert _tags == _expected


@pytest.mark.django_db
def test_util_tag_tool_projects(project0, project1, resourceX):
    tag_tool = TagTool(
        TagsTool(),
        name=None,
        pk=None,
        priority=None,
        project=None,
        slug=None)
    _patch_ctx = patch(
        'pontoon.tags.utils.TagTool.resources',
        new_callable=PropertyMock)
    with _patch_ctx as m:
        _m = MagicMock()
        _m.values_list.return_value = Resource.objects.filter(
            project__in=[
                project0.pk,
                resourceX.project.pk]).values_list('project')
        m.return_value = _m
        projects = tag_tool.projects
        assert isinstance(projects, QuerySet)
        assert (
            sorted(projects.values_list('pk', flat=True))
            == sorted([project0.pk, resourceX.project.pk]))


@pytest.mark.django_db
def test_util_tag_tool_locales(locale0, locale1, translated_resourceX):
    tag_tool = TagTool(
        TagsTool(),
        name=None,
        pk=None,
        priority=None,
        project=None,
        slug=None)
    _patch_ctx = patch(
        'pontoon.tags.utils.TagTool.resources',
        new_callable=PropertyMock)
    with _patch_ctx as m:
        _m = MagicMock()
        _m.values_list.return_value = Resource.objects.filter(
            translatedresources__locale__in=[
                locale0.pk,
                translated_resourceX.locale.pk]).values_list(
                    'translatedresources__locale')
        m.return_value = _m
        locales = tag_tool.locales
        assert isinstance(locales, QuerySet)
        assert (
            sorted(locales.values_list('pk', flat=True))
            == sorted([locale0.pk, translated_resourceX.locale.pk]))


@pytest.mark.django_db
def test_util_tag_tool_iter_resource_paths(resource0, project1, locale0,
                                           translated_resourceX,
                                           translated_resource_factory):
    project0 = resource0.project
    resourceX = translated_resourceX.resource
    projectX = resourceX.project
    tag_tool = TagTool(
        TagsTool(),
        name=None,
        pk=None,
        priority=None,
        project=None,
        slug=None)
    _patch_ctx = patch(
        'pontoon.tags.utils.TagTool.resources',
        new_callable=PropertyMock)

    # ensure that the paths are distinct,
    # by adding some duplicating translated resources
    translated_resource_factory(
        batch_kwargs=[dict(resource=resourceX, locale=locale0)] * 3)

    with _patch_ctx as m:
        _m = MagicMock()
        _m.values_list.return_value = TranslatedResource.objects.filter(
            resource__project__in=[project0.pk, projectX.pk]).values_list(
                'resource__project__slug', 'resource__path')
        m.return_value = _m
        paths = tag_tool.iter_resource_paths()
        isinstance(paths, types.GeneratorType)
        assert (
            sorted(list(paths))
            == sorted(
                [(projectX.slug, resourceX.path),
                 (project0.slug, resource0.path)]))


@pytest.mark.django_db
def test_util_tag_tool_get_resource_stats(tag_matrix):
    tag_tool = TagTool(
        TagsTool(),
        name=None,
        pk=None,
        priority=None,
        project=None,
        slug=None)
    resource_stats = tag_tool.get_resource_stats()
    assert isinstance(resource_stats, TagsTool)
    assert (
        resource_stats.groupby
        == ['resource'])
    assert (
        resource_stats.stat_tool.groupby
        == ['pk', 'resource'])

    data = resource_stats.stat_tool.data
    # no dupes
    assert (
        len(set([(d['pk'], d['resource']) for d in data]))
        == len([(d['pk'], d['resource']) for d in data]))
    assert tag_tool.resource_stats == data


@pytest.mark.django_db
def test_util_tag_tool_get_project_stats(tag_matrix, tag_test_kwargs):
    name, kwargs = tag_test_kwargs
    tags_tool = TagsTool(**kwargs)
    if not len(tags_tool):
        assert "no_match" in name
        return
    tag_tool = list(tags_tool)[0]
    project_stats = tag_tool.get_project_stats()
    assert isinstance(project_stats, TagsTool)
    assert (
        project_stats.groupby
        == ['resource__project'])
    assert (
        project_stats.stat_tool.groupby
        == ['pk', 'resource__project'])
    data = project_stats.stat_tool.data
    # no dupes
    assert (
        len(set([(d['pk'], d['resource__project']) for d in data]))
        == len([(d['pk'], d['resource__project']) for d in data]))
    assert tag_tool.project_stats == data


def test_util_tag_tool_resources_stats():
    tag_tool = TagTool(
        TagsTool(),
        name=None,
        pk=None,
        priority=None,
        project=None,
        slug=None)
    _patch_ctx = patch(
        'pontoon.tags.utils.TagTool.get_resource_stats')
    with _patch_ctx as m:
        _p1 = PropertyMock(return_value=(1, 2, 3))
        _m1 = MagicMock()
        type(_m1).data = _p1
        _p0 = PropertyMock(return_value=_m1)
        _m0 = MagicMock()
        type(_m0).stat_tool = _p0
        m.return_value = _m0
        result = tag_tool.resource_stats
        assert result == (1, 2, 3)
        assert _p1.called
        _p1.reset_mock()
        _p1.return_value = (4, 5, 6)
        result = tag_tool.resource_stats
        assert not _p1.called
        assert result == (1, 2, 3)
        del tag_tool.__dict__["resource_stats"]
        result = tag_tool.resource_stats
        assert _p1.called
        assert result == (4, 5, 6)


def test_util_tag_tool_projects_stats():
    tag_tool = TagTool(
        TagsTool(),
        name=None,
        pk=None,
        priority=None,
        project=None,
        slug=None)
    _patch_ctx = patch(
        'pontoon.tags.utils.TagTool.get_project_stats')
    with _patch_ctx as m:
        _p1 = PropertyMock(return_value=(1, 2, 3))
        _m1 = MagicMock()
        type(_m1).data = _p1
        _p0 = PropertyMock(return_value=_m1)
        _m0 = MagicMock()
        type(_m0).stat_tool = _p0
        m.return_value = _m0
        result = tag_tool.project_stats
        assert result == (1, 2, 3)
        assert _p1.called
        _p1.reset_mock()
        _p1.return_value = (4, 5, 6)
        result = tag_tool.project_stats
        assert not _p1.called
        assert result == (1, 2, 3)
        del tag_tool.__dict__["project_stats"]
        result = tag_tool.project_stats
        assert _p1.called
        assert result == (4, 5, 6)


def test_util_tag_tool_iter_resources():
    tag_tool = TagTool(
        TagsTool(),
        name=None,
        pk=None,
        priority=None,
        project=None,
        slug=None)
    _patch_ctx = nested(
        patch(
            'pontoon.tags.utils.TagTool.resource_stats',
            new_callable=PropertyMock),
        patch('pontoon.tags.utils.TaggedResource'))
    with _patch_ctx as (m_stats, m_resource):
        m_stats.return_value = [dict(foo=1), dict(foo=2), dict(foo=3)]
        m_resource.return_value = "X"
        resources = tag_tool.iter_resources()
        assert isinstance(resources, types.GeneratorType)
        result = list(resources)
        assert m_stats.called
        assert result == ['X'] * 3
        assert len(m_resource.call_args_list) == 3
        for i, args in enumerate(m_resource.call_args_list):
            assert args[1]['foo'] == i + 1


def test_util_tag_tool_iter_projects():
    tag_tool = TagTool(
        TagsTool(),
        name=None,
        pk=None,
        priority=None,
        project=None,
        slug=None)
    _patch_ctx = nested(
        patch(
            'pontoon.tags.utils.TagTool.project_stats',
            new_callable=PropertyMock),
        patch('pontoon.tags.utils.TaggedProject'))
    with _patch_ctx as (m_stats, m_project):
        m_stats.return_value = [dict(foo=1), dict(foo=2), dict(foo=3)]
        m_project.return_value = "X"
        projects = tag_tool.iter_projects()
        assert isinstance(projects, types.GeneratorType)
        result = list(projects)
        assert m_stats.called
        assert result == ['X'] * 3
        assert len(m_project.call_args_list) == 3
        for i, args in enumerate(m_project.call_args_list):
            assert args[1]['foo'] == i + 1
