
import fnmatch

import pytest

from mock import MagicMock, PropertyMock, patch

from django.db.models import QuerySet

from pontoon.base.models import Resource
from pontoon.base.utils import glob_to_regex

from pontoon.tags.exceptions import InvalidProjectError
from pontoon.tags.models import Tag
from pontoon.tags.utils import TagsResourcesTool


def test_util_tags_resources_tool(tag_init_kwargs):
    # tests instantiation of resources tool
    kwargs = tag_init_kwargs
    resources_tool = TagsResourcesTool(**kwargs)
    for k, v in kwargs.items():
        assert getattr(resources_tool, k) == v
    assert resources_tool.data_manager == Resource.objects
    assert resources_tool.filter_methods == (
        'locales', 'projects', 'slug', 'path')


@pytest.mark.django_db
def test_util_tags_resources_tool_filtered_data(tag_matrix, tag_test_kwargs):
    # tests getting resources for given filters
    name, kwargs = tag_test_kwargs
    resources_tool = TagsResourcesTool(**kwargs)
    expected = resources_tool.data_manager.all()
    if 'projects' in kwargs:
        expected = expected.filter(project__in=kwargs['projects'])
    if 'locales' in kwargs:
        expected = expected.filter(
            translatedresources__locale__in=kwargs["locales"]).distinct()
    if 'slug' in kwargs:
        expected = expected.filter(
            tag__slug__regex=glob_to_regex(kwargs['slug'])).distinct()
    if kwargs.get("path"):
        expected = list(
            t.pk for t
            in expected.order_by('pk')
            if fnmatch.fnmatch(t.path, kwargs["path"]))
    else:
        expected = list(expected.order_by('pk').values_list('pk', flat=True))
    result = resources_tool.filtered_data
    assert isinstance(result, QuerySet)
    assert (
        sorted(list(result.values_list('pk', flat=True)))
        == expected)


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
def test_util_tags_resources_tool_link(resource0, tagX):
    resource_tool = TagsResourcesTool()

    assert tagX.resources.count() == 0
    resource_tool.link(tagX.slug, '*')
    assert tagX.resources.count() == Resource.objects.count()

    tagX.resources.remove(*list(tagX.resources.all()))
    resource_tool.link(tagX.slug, resource0.path)
    assert tagX.resources.count() == 1
    assert resource0 in tagX.resources.all()


@pytest.mark.django_db
def test_util_tags_resources_tool_link_project(resource0, tagX):
    resource_tool = TagsResourcesTool(projects=[resource0.project])
    assert tagX.resources.count() == 0
    resource_tool.link(tagX.slug, '*')
    assert (
        tagX.resources.count()
        == Resource.objects.filter(project=resource0.project).count())


@pytest.mark.django_db
def test_util_tags_resources_tool_link_bad(resource0, tagX, project1):
    resource_tool = TagsResourcesTool()
    tagX.project = project1
    tagX.save()
    with pytest.raises(InvalidProjectError):
        resource_tool.link(tagX.slug, resource0.path)
    with pytest.raises(InvalidProjectError):
        resource_tool.link(tagX.slug, "*")
    with pytest.raises(InvalidProjectError):
        resource_tool.link(
            tagX.slug,
            resources=[
                dict(project=resource0.project.id,
                     path=resource0.path)])


@pytest.mark.django_db
def test_util_tags_resources_tool_linked_resources(resource0, tagX):
    resource_tool = TagsResourcesTool()

    _patch_ctx = patch(
        'pontoon.tags.utils.TagsResourcesTool.get')
    with _patch_ctx as m:
        values = MagicMock()
        values.values.return_value = 7
        m.return_value = values
        linked = resource_tool.get_linked_resources(23)
        assert linked == 7
        assert list(m.call_args) == [(23,), {}]
        assert (
            list(values.values.call_args)
            == [('path', 'project'), {}])


@pytest.mark.django_db
def test_util_tags_resources_tool_linkable_resources(resource0, tagX):
    resource_tool = TagsResourcesTool()

    _patch_ctx = patch(
        'pontoon.tags.utils.TagsResourcesTool.find')
    with _patch_ctx as m:
        values = MagicMock()
        values.values.return_value = 7
        m.return_value = values
        linkable = resource_tool.get_linkable_resources(23)
        assert linkable == 7
        assert list(m.call_args) == [('*',), {'exclude': 23}]
        assert (
            list(values.values.call_args)
            == [('path', 'project'), {}])


@pytest.mark.django_db
def test_util_tags_resources_tool_link_paths(resource0, tagX):
    resource_tool = TagsResourcesTool()

    assert tagX.resources.count() == 0
    resource_tool.link(
        tagX.slug,
        resources=Resource.objects.values("project", "path"))
    assert tagX.resources.count() == Resource.objects.count()

    tagX.resources.remove(*list(tagX.resources.all()))
    resource_tool.link(
        tagX.slug,
        resources=[dict(project=resource0.project.pk, path=resource0.path)])
    assert tagX.resources.count() == 1
    assert resource0 in tagX.resources.all()


@pytest.mark.django_db
def test_util_tags_resources_tool_unlink(tag0, resourceX):
    resource0 = tag0.resources.first()
    resource_tool = TagsResourcesTool()

    tag0.resources.add(resourceX)
    assert tag0.resources.count() == 2
    resource_tool.unlink(tag0.slug, '*')
    assert tag0.resources.count() == 0

    tag0.resources.add(resource0, resourceX)
    resource_tool.unlink(tag0.slug, resource0.path)
    assert tag0.resources.count() == 1
    assert resourceX in tag0.resources.all()


@pytest.mark.django_db
def test_util_tags_resources_tool_unlink_paths(tag0, resource0, resourceX):
    resource0 = tag0.resources.first()
    resource_tool = TagsResourcesTool()

    tag0.resources.add(resourceX)
    assert tag0.resources.count() == 2
    resource_tool.unlink(
        tag0.slug,
        resources=tag0.resources.values('project', 'path'))
    assert tag0.resources.count() == 0

    tag0.resources.add(resource0, resourceX)
    resource_tool.unlink(
        tag0.slug,
        resources=[
            dict(project=resource0.project.pk, path=resource0.path)])
    assert tag0.resources.count() == 1
    assert resourceX in tag0.resources.all()


def test_util_tag_resources_tool_get():
    resource_tool = TagsResourcesTool()

    _patch_ctx = patch(
        'pontoon.tags.utils.TagsResourcesTool.filtered_data',
        new_callable=PropertyMock())
    with _patch_ctx as p:
        _m2 = MagicMock()
        _m2.distinct.return_value = 23
        p.filter.return_value = _m2
        result = resource_tool.get('FOO')
        assert result == 23
        assert (
            list(p.filter.call_args)
            == [(), {'tag__slug': 'FOO'}])
