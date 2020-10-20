import fnmatch
from unittest.mock import MagicMock, PropertyMock, patch

import pytest

from django.db.models import QuerySet

from pontoon.base.models import Resource
from pontoon.test.factories import (
    ResourceFactory,
    TagFactory,
)
from pontoon.tags.exceptions import InvalidProjectError
from pontoon.tags.models import Tag
from pontoon.tags.utils import TagsResourcesTool


@pytest.fixture
def resource_c(project_a):
    return ResourceFactory.create(project=project_a, path="resource_c.po", format="po")


@pytest.fixture
def tag_b(resource_b):
    tag = TagFactory.create(slug="tag_b", name="Other Tag")
    tag.resources.add(resource_b)
    return tag


@pytest.fixture
def tag_c():
    tag = TagFactory.create(slug="tag_b", name="Other Tag")
    return tag


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            "locales": None,
            "path": None,
            "priority": None,
            "projects": None,
            "slug": None,
        },
        {"locales": 1, "path": 2, "priority": 3, "projects": 4, "slug": 5},
    ],
)
def test_util_tags_resources_tool(kwargs):
    # tests instantiation of resources tool
    resources_tool = TagsResourcesTool(**kwargs)
    for k, v in kwargs.items():
        assert getattr(resources_tool, k) == v
    assert resources_tool.data_manager == Resource.objects
    assert resources_tool.filter_methods == ("locales", "projects", "slug", "path")


@pytest.mark.django_db
def test_util_tags_resources_tool_filtered_data(tag_matrix, tag_test_kwargs):
    # tests getting resources for given filters
    name, kwargs = tag_test_kwargs
    resources_tool = TagsResourcesTool(**kwargs)
    expected = resources_tool.data_manager.all()
    if "projects" in kwargs:
        expected = expected.filter(project__in=kwargs["projects"])
    if "locales" in kwargs:
        expected = expected.filter(
            translatedresources__locale__in=kwargs["locales"]
        ).distinct()
    if "slug" in kwargs:
        expected = expected.filter(tag__slug__contains=kwargs["slug"]).distinct()
    if kwargs.get("path"):
        expected = list(
            t.pk
            for t in expected.order_by("pk")
            if fnmatch.fnmatch(t.path, kwargs["path"])
        )
    else:
        expected = list(expected.order_by("pk").values_list("pk", flat=True))
    result = resources_tool.filtered_data
    assert isinstance(result, QuerySet)
    assert sorted(list(result.values_list("pk", flat=True))) == expected


@pytest.mark.parametrize(
    "kwargs", [dict(), dict(projects=1, path=2)],
)
def test_util_tags_resources_tool_params(kwargs):
    resource_tool = TagsResourcesTool(**kwargs)
    for k in ["projects", "path"]:
        assert getattr(resource_tool, k) == kwargs.get(k)
    assert resource_tool.tag_manager == Tag.objects
    assert resource_tool.resource_manager == Resource.objects


@pytest.mark.django_db
def test_util_tags_resources_tool_find(tag_a, tag_b):
    resource_tool = TagsResourcesTool()

    data = resource_tool.find()
    assert isinstance(data, QuerySet)
    assert data.count() == Resource.objects.count()

    resource = tag_a.resources.first()
    data = resource_tool.find(resource.path)
    assert isinstance(data, QuerySet)
    assert data.count() == 1
    assert data[0] == resource

    data = resource_tool.find(exclude=tag_a.slug)
    assert isinstance(data, QuerySet)
    assert data.count()
    assert resource not in data

    data = resource_tool.find(include=tag_a.slug)
    assert isinstance(data, QuerySet)
    assert data.count() == 1
    assert resource in data

    resource_tool = TagsResourcesTool(projects=[resource.project])
    data = resource_tool.find()
    assert data.count() == Resource.objects.filter(project=resource.project).count()
    assert data[0].project == resource.project


@pytest.mark.django_db
def test_util_tags_resources_tool_link_project(resource_a, tag_c):
    resource_tool = TagsResourcesTool(projects=[resource_a.project])
    tag_c.project = resource_a.project
    tag_c.save()
    assert tag_c.resources.count() == 0
    resource_tool.link(
        tag_c.slug,
        resources=[{"project": resource_a.project.pk, "path": resource_a.path}],
    )
    assert (
        tag_c.resources.count()
        == Resource.objects.filter(project=resource_a.project).count()
    )


@pytest.mark.django_db
def test_util_tags_resources_tool_link_bad(resource_a, tag_c, project_b):
    resource_tool = TagsResourcesTool()
    tag_c.project = project_b
    tag_c.save()
    with pytest.raises(InvalidProjectError):
        resource_tool.link(
            tag_c.slug,
            resources=[{"project": resource_a.project.pk, "path": resource_a.path}],
        )
    with pytest.raises(InvalidProjectError):
        resource_tool.link(
            tag_c.slug,
            resources=[{"project": resource_a.project.pk, "path": resource_a.path}],
        )


@pytest.mark.django_db
def test_util_tags_resources_tool_linked_resources(resource_a, tag_c):
    resource_tool = TagsResourcesTool()

    _patch_ctx = patch("pontoon.tags.utils.TagsResourcesTool.get")
    with _patch_ctx as m:
        values = MagicMock()
        values.values.return_value = 7
        m.return_value = values
        linked = resource_tool.get_linked_resources(23)
        assert linked == 7
        assert list(m.call_args) == [(23,), {}]
        assert list(values.values.call_args) == [("path", "project"), {}]


@pytest.mark.django_db
def test_util_tags_resources_tool_linkable_resources(resource_a, tag_c):
    resource_tool = TagsResourcesTool()

    _patch_ctx = patch("pontoon.tags.utils.TagsResourcesTool.find")
    with _patch_ctx as m:
        values = MagicMock()
        values.values.return_value = 7
        m.return_value = values
        linkable = resource_tool.get_linkable_resources(23)
        assert linkable == 7
        assert list(m.call_args) == [tuple(), {"exclude": 23}]
        assert list(values.values.call_args) == [("path", "project"), {}]


@pytest.mark.django_db
def test_util_tags_resources_tool_link_paths(resource_a, tag_c):
    resource_tool = TagsResourcesTool()

    assert tag_c.resources.count() == 0
    resource_tool.link(tag_c.slug, resources=Resource.objects.values("project", "path"))
    assert tag_c.resources.count() == Resource.objects.count()

    tag_c.resources.remove(*list(tag_c.resources.all()))
    resource_tool.link(
        tag_c.slug,
        resources=[dict(project=resource_a.project.pk, path=resource_a.path)],
    )
    assert tag_c.resources.count() == 1
    assert resource_a in tag_c.resources.all()


@pytest.mark.django_db
def test_util_tags_resources_tool_unlink(tag_a, resource_c):
    resource = tag_a.resources.first()
    resource_tool = TagsResourcesTool()

    tag_a.resources.add(resource_c)
    assert tag_a.resources.count() == 2

    tag_a.resources.add(resource, resource_c)
    resource_tool.unlink(
        tag_a.slug, [{"project": resource.project.pk, "path": resource.path}]
    )
    assert tag_a.resources.count() == 1
    assert resource_c in tag_a.resources.all()


@pytest.mark.django_db
def test_util_tags_resources_tool_unlink_paths(tag_a, resource_a, resource_c):
    resource_a = tag_a.resources.first()
    resource_tool = TagsResourcesTool()

    tag_a.resources.add(resource_c)
    assert tag_a.resources.count() == 2
    resource_tool.unlink(
        tag_a.slug, resources=tag_a.resources.values("project", "path")
    )
    assert tag_a.resources.count() == 0

    tag_a.resources.add(resource_a, resource_c)
    resource_tool.unlink(
        tag_a.slug,
        resources=[dict(project=resource_a.project.pk, path=resource_a.path)],
    )
    assert tag_a.resources.count() == 1
    assert resource_c in tag_a.resources.all()


def test_util_tag_resources_tool_get():
    resource_tool = TagsResourcesTool()

    _patch_ctx = patch(
        "pontoon.tags.utils.TagsResourcesTool.filtered_data",
        new_callable=PropertyMock(),
    )
    with _patch_ctx as p:
        _m2 = MagicMock()
        _m2.distinct.return_value = 23
        p.filter.return_value = _m2
        result = resource_tool.get("FOO")
        assert result == 23
        assert list(p.filter.call_args) == [(), {"tag__slug": "FOO"}]
