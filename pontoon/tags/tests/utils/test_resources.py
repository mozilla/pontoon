import factory
import fnmatch
import pytest
from mock import MagicMock, PropertyMock, patch

from django.contrib.auth import get_user_model
from django.db.models import QuerySet

from pontoon.base.models import (
    Locale,
    Project,
    ProjectLocale,
    Resource,
    TranslatedResource,
)
from pontoon.base.utils import glob_to_regex
from pontoon.tags.exceptions import InvalidProjectError
from pontoon.tags.models import Tag
from pontoon.tags.utils import TagsResourcesTool


class UserFactory(factory.DjangoModelFactory):
    class Meta:
        model = get_user_model()


@pytest.fixture
def fake_user():
    return UserFactory(
        username="fake_user",
        email="fake_user@example.org"
    )


@pytest.fixture
def member(client, fake_user):
    client.force_login(fake_user)
    return client


@pytest.fixture
def admin():
    """Admin - a superuser"""
    return get_user_model().objects.create(
        username="admin",
        email="admin@example.org",
        is_superuser=True,
    )


@pytest.fixture
def locale():
    return Locale.objects.create(
        code="kg",
        name="Klingon",
    )


@pytest.fixture
def project():
    return Project.objects.create(
        slug="project", name="Project"
    )


@pytest.fixture
def other_project():
    return Project.objects.create(
        slug="other_project", name="Other Project"
    )


@pytest.fixture
def resource(project, locale, fake_user):
    # Tags require a ProjectLocale to work.
    ProjectLocale.objects.create(project=project, locale=locale)
    resource = Resource.objects.create(
        project=project, path="resource.po", format="po"
    )
    # Tags require a TranslatedResource to work.
    TranslatedResource.objects.create(
        resource=resource, locale=locale
    )
    resource.total_strings = 1
    resource.save()
    return resource


@pytest.fixture
def other_resource(project, locale):
    resource = Resource.objects.create(
        project=project, path="other_resource.po", format="po"
    )
    # Tags require a TranslatedResource to work.
    TranslatedResource.objects.create(
        resource=resource, locale=locale
    )
    resource.total_strings = 1
    resource.save()
    return resource


@pytest.fixture
def third_resource(project, locale):
    return Resource.objects.create(
        project=project, path="third_resource.po", format="po"
    )


@pytest.fixture
def tag(resource):
    tag = Tag.objects.create(slug="tag", name="Tag")
    tag.resources.add(resource)
    return tag


@pytest.fixture
def other_tag(other_resource):
    tag = Tag.objects.create(slug="other_tag", name="Other Tag")
    tag.resources.add(other_resource)
    return tag


@pytest.fixture
def third_tag():
    tag = Tag.objects.create(slug="other_tag", name="Other Tag")
    return tag


@pytest.mark.parametrize(
    "kwargs",
    [
        {
            'locales': None,
            'path': None,
            'priority': None,
            'projects': None,
            'slug': None,
        },
        {
            'locales': 1,
            'path': 2,
            'priority': 3,
            'projects': 4,
            'slug': 5,
        },
    ],
)
def test_util_tags_resources_tool(kwargs):
    # tests instantiation of resources tool
    resources_tool = TagsResourcesTool(**kwargs)
    for k, v in kwargs.items():
        assert getattr(resources_tool, k) == v
    assert resources_tool.data_manager == Resource.objects
    assert resources_tool.filter_methods == (
        'locales', 'projects', 'slug', 'path'
    )


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
            translatedresources__locale__in=kwargs["locales"]
        ).distinct()
    if 'slug' in kwargs:
        expected = expected.filter(
            tag__slug__regex=glob_to_regex(kwargs['slug'])
        ).distinct()
    if kwargs.get("path"):
        expected = list(
            t.pk for t
            in expected.order_by('pk')
            if fnmatch.fnmatch(t.path, kwargs["path"])
        )
    else:
        expected = list(expected.order_by('pk').values_list('pk', flat=True))
    result = resources_tool.filtered_data
    assert isinstance(result, QuerySet)
    assert (
        sorted(list(result.values_list('pk', flat=True)))
        == expected
    )


@pytest.mark.parametrize(
    "kwargs",
    [
        dict(),
        dict(projects=1, path=2),
    ],
)
def test_util_tags_resources_tool_params(kwargs):
    resource_tool = TagsResourcesTool(**kwargs)
    for k in ['projects', 'path']:
        assert getattr(resource_tool, k) == kwargs.get(k)
    assert resource_tool.tag_manager == Tag.objects
    assert resource_tool.resource_manager == Resource.objects


@pytest.mark.django_db
def test_util_tags_resources_tool_find(tag, other_tag):
    resource_tool = TagsResourcesTool()

    data = resource_tool.find('*')
    assert isinstance(data, QuerySet)
    assert data.count() == Resource.objects.count()

    resource = tag.resources.first()
    data = resource_tool.find(resource.path)
    assert isinstance(data, QuerySet)
    assert data.count() == 1
    assert data[0] == resource

    data = resource_tool.find('*', exclude=tag.slug)
    assert isinstance(data, QuerySet)
    assert data.count()
    assert resource not in data

    data = resource_tool.find('*', include=tag.slug)
    assert isinstance(data, QuerySet)
    assert data.count() == 1
    assert resource in data

    resource_tool = TagsResourcesTool(projects=[resource.project])
    data = resource_tool.find('*')
    assert (
        data.count()
        == Resource.objects.filter(project=resource.project).count()
    )
    assert data[0].project == resource.project


@pytest.mark.django_db
def test_util_tags_resources_tool_link(resource, third_tag):
    resource_tool = TagsResourcesTool()

    assert third_tag.resources.count() == 0
    resource_tool.link(third_tag.slug, '*')
    assert third_tag.resources.count() == Resource.objects.count()

    third_tag.resources.remove(*list(third_tag.resources.all()))
    resource_tool.link(third_tag.slug, resource.path)
    assert third_tag.resources.count() == 1
    assert resource in third_tag.resources.all()


@pytest.mark.django_db
def test_util_tags_resources_tool_link_project(resource, third_tag):
    resource_tool = TagsResourcesTool(projects=[resource.project])
    assert third_tag.resources.count() == 0
    resource_tool.link(third_tag.slug, '*')
    assert (
        third_tag.resources.count()
        == Resource.objects.filter(project=resource.project).count()
    )


@pytest.mark.django_db
def test_util_tags_resources_tool_link_bad(resource, third_tag, other_project):
    resource_tool = TagsResourcesTool()
    third_tag.project = other_project
    third_tag.save()
    with pytest.raises(InvalidProjectError):
        resource_tool.link(third_tag.slug, resource.path)
    with pytest.raises(InvalidProjectError):
        resource_tool.link(third_tag.slug, "*")
    with pytest.raises(InvalidProjectError):
        resource_tool.link(
            third_tag.slug,
            resources=[{
                'project': resource.project.id,
                'path': resource.path,
            }]
        )


@pytest.mark.django_db
def test_util_tags_resources_tool_linked_resources(resource, third_tag):
    resource_tool = TagsResourcesTool()

    _patch_ctx = patch(
        'pontoon.tags.utils.TagsResourcesTool.get'
    )
    with _patch_ctx as m:
        values = MagicMock()
        values.values.return_value = 7
        m.return_value = values
        linked = resource_tool.get_linked_resources(23)
        assert linked == 7
        assert list(m.call_args) == [(23,), {}]
        assert (
            list(values.values.call_args)
            == [('path', 'project'), {}]
        )


@pytest.mark.django_db
def test_util_tags_resources_tool_linkable_resources(resource, third_tag):
    resource_tool = TagsResourcesTool()

    _patch_ctx = patch(
        'pontoon.tags.utils.TagsResourcesTool.find'
    )
    with _patch_ctx as m:
        values = MagicMock()
        values.values.return_value = 7
        m.return_value = values
        linkable = resource_tool.get_linkable_resources(23)
        assert linkable == 7
        assert list(m.call_args) == [('*',), {'exclude': 23}]
        assert (
            list(values.values.call_args)
            == [('path', 'project'), {}]
        )


@pytest.mark.django_db
def test_util_tags_resources_tool_link_paths(resource, third_tag):
    resource_tool = TagsResourcesTool()

    assert third_tag.resources.count() == 0
    resource_tool.link(
        third_tag.slug,
        resources=Resource.objects.values("project", "path")
    )
    assert third_tag.resources.count() == Resource.objects.count()

    third_tag.resources.remove(*list(third_tag.resources.all()))
    resource_tool.link(
        third_tag.slug,
        resources=[dict(project=resource.project.pk, path=resource.path)]
    )
    assert third_tag.resources.count() == 1
    assert resource in third_tag.resources.all()


@pytest.mark.django_db
def test_util_tags_resources_tool_unlink(tag, third_resource):
    resource = tag.resources.first()
    resource_tool = TagsResourcesTool()

    tag.resources.add(third_resource)
    assert tag.resources.count() == 2
    resource_tool.unlink(tag.slug, '*')
    assert tag.resources.count() == 0

    tag.resources.add(resource, third_resource)
    resource_tool.unlink(tag.slug, resource.path)
    assert tag.resources.count() == 1
    assert third_resource in tag.resources.all()


@pytest.mark.django_db
def test_util_tags_resources_tool_unlink_paths(tag, resource, third_resource):
    resource = tag.resources.first()
    resource_tool = TagsResourcesTool()

    tag.resources.add(third_resource)
    assert tag.resources.count() == 2
    resource_tool.unlink(
        tag.slug,
        resources=tag.resources.values('project', 'path')
    )
    assert tag.resources.count() == 0

    tag.resources.add(resource, third_resource)
    resource_tool.unlink(
        tag.slug,
        resources=[
            dict(project=resource.project.pk, path=resource.path)
        ]
    )
    assert tag.resources.count() == 1
    assert third_resource in tag.resources.all()


def test_util_tag_resources_tool_get():
    resource_tool = TagsResourcesTool()

    _patch_ctx = patch(
        'pontoon.tags.utils.TagsResourcesTool.filtered_data',
        new_callable=PropertyMock()
    )
    with _patch_ctx as p:
        _m2 = MagicMock()
        _m2.distinct.return_value = 23
        p.filter.return_value = _m2
        result = resource_tool.get('FOO')
        assert result == 23
        assert (
            list(p.filter.call_args)
            == [(), {'tag__slug': 'FOO'}]
        )
