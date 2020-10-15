import functools
from collections import OrderedDict
from datetime import datetime

import pytest

from django.db.models import F
from django.utils import timezone

from pontoon.base.models import TranslatedResource, Translation
from pontoon.tags.models import Tag
from .site import _factory


def tag_factory():
    def instance_attrs(instance, i):
        if not instance.slug:
            instance.slug = "factorytag%s" % i
        if not instance.name:
            instance.name = "Factory Tag %s" % i

    return functools.partial(_factory, Model=Tag, instance_attrs=instance_attrs)


def _assert_tags(expected, data):
    assert len(expected) == len(data)
    results = dict((d["slug"], d) for d in data)
    attrs = [
        "pk",
        "name",
        # "last_change",
        "total_strings",
        "approved_strings",
        "unreviewed_strings",
        "fuzzy_strings",
    ]
    for slug, stats in results.items():
        _exp = expected[slug]
        for attr in attrs:
            assert _exp[attr] == stats[attr]


@pytest.fixture
def assert_tags():
    """This fixture provides a function for comparing calculated
    tag stats against those provided by the tags tool
    """
    return _assert_tags


def _calculate_resource_tags(**kwargs):
    # returns the tags associated with a given resource, filters
    # on priority if given
    priority = kwargs.get("priority", None)
    resource_tags = {}
    tags_through = Tag.resources.through.objects.values_list(
        "resource", "tag", "tag__slug", "tag__name",
    )
    if priority is not None:
        if priority is True:
            tags_through = tags_through.exclude(tag__priority__isnull=True)
        elif priority is False:
            tags_through = tags_through.exclude(tag__priority__isnull=False)
        else:
            tags_through = tags_through.filter(tag__priority=priority)

    for resource, tag, _slug, name in tags_through.iterator():
        resource_tags[resource] = resource_tags.get(resource, []) + [(tag, _slug, name)]
    return resource_tags


def _tag_iterator(things, **kwargs):
    # for given qs.values() (`things`) and **kwargs to filter on, this will
    # find and iterate matching tags.
    # `things` can  be either translations or translated_resources, but
    # they must have their `locale`, `project`, `resource` and
    # `resource.path` denormalized where required.
    locales = list(l.id for l in kwargs.get("locales", []))
    projects = list(p.id for p in kwargs.get("projects", []))
    slug = kwargs.get("slug", None)
    path = kwargs.get("path", None)
    resource_tags = _calculate_resource_tags(**kwargs)

    for thing in things.iterator():
        if locales and thing["locale"] not in locales:
            continue
        if projects and thing["project"] not in projects:
            continue
        if path and path not in thing["path"]:
            continue
        for tag in resource_tags.get(thing["resource"], []):
            __, _slug, __ = tag
            if slug and slug not in _slug:
                continue
            yield thing, tag


def _calculate_tags(**kwargs):
    # calculate what the stats per-tag with given **kwargs should be
    # the long-hand way
    trs = TranslatedResource.objects.all()
    attrs = [
        "approved_strings",
        "unreviewed_strings",
        "fuzzy_strings",
    ]
    totals = {}
    resource_attrs = [
        "resource",
        "locale",
        "latest_translation__date",
    ]
    annotations = dict(
        total_strings=F("resource__total_strings"),
        project=F("resource__project"),
        path=F("resource__path"),
    )
    # this is a `values` of translated resources, with the project, path
    # and total_strings denormalized to project/path/total_strings.
    qs = trs.values(*resource_attrs + attrs).annotate(**annotations)
    translated_resource_tags = _tag_iterator(qs, **kwargs)
    attrs = ["total_strings"] + attrs
    # iterate through associated tags for all matching translated resources
    for tr, (_pk, _slug, _name) in translated_resource_tags:
        if kwargs.get("groupby"):
            key = tr[kwargs["groupby"]]
        else:
            key = _slug
        if key not in totals:
            # create a totals[tag] with zeros for this tag
            totals[key] = dict((attr, 0) for attr in attrs)
            totals[key].update(dict(name=_name, pk=_pk, last_change=None))
        for attr in attrs:
            # add the total for this translated resource to the tags total
            totals[key][attr] += tr[attr]
    return totals


@pytest.fixture
def calculate_tags():
    """This fixture provides a function for calculating the tags and their
    expected stats etc currently in the database, after filtering for
    provided **kwargs
    """
    return _calculate_tags


def _calculate_tags_latest(**kwargs):
    # calculate what the latest events per-tag with given **kwargs should be
    # the long-hand way
    translations = Translation.objects.all()
    latest_dates = {}

    translation_attrs = [
        "pk",
        "date",
        "locale",
    ]
    annotations = dict(
        resource=F("entity__resource"),
        path=F("entity__resource__path"),
        project=F("entity__resource__project"),
    )
    # this is a `values` of translations, with the resource, path and project
    # denormalized to resource/path/project.
    qs = translations.values(*translation_attrs).annotate(**annotations)
    translation_tags = _tag_iterator(qs, **kwargs)
    # iterate through associated tags for all matching translations
    for translation, (tag, __, __) in translation_tags:
        if kwargs.get("groupby"):
            key = translation[kwargs["groupby"]]
        else:
            key = tag
        # get the current latest for this tag
        _pk, _date = latest_dates.get(key, (None, timezone.make_aware(datetime.min)))
        if translation["date"] > _date:
            # set this translation if its newer than the current latest
            # for this tag
            latest_dates[key] = (translation["pk"], translation["date"])
    return latest_dates


@pytest.fixture
def calculate_tags_latest():
    """This fixture provides a function for calculating the tags and their
    expected latest changes currently in the database, after filtering for
    provided **kwargs
    """
    return _calculate_tags_latest


@pytest.fixture
def tag_matrix(site_matrix):
    """This provides the `site_matrix` fixture but with added tags.

    This fixture can be used in conjunction with the `calculate_tags`
    fixture to test for tags using kwargs from the parametrized
    `tag_test_kwargs` fixture

    """
    factories = site_matrix["factories"]
    factories["tag"] = tag_factory()

    # this creates 113 tags
    # every 20th tag gets no priority
    # the others get between 0-5
    tags = factories["tag"](
        args=[
            {"priority": (None if not i or not (i % 20) else int(i / 20))}
            for i in range(0, 113)
        ]
    )

    # associate tags with resources
    for i, resource in enumerate(site_matrix["resources"]):
        x = 0
        indeces = []
        # this distributes the tags amongst resources in
        # a fairly arbitrary fashion
        # every resource gets the tag with index of 0
        while True:
            idx = x * (i + 1)
            if idx >= len(tags):
                break
            indeces.append(idx)
            x = x + 1
        # add tags to the resource's tag_set
        resource.tag_set.add(*[tags[n] for n in indeces])
    site_matrix["tags"] = tags
    return site_matrix


_tag_kwargs = OrderedDict(
    (
        ("empty", dict()),
        ("project0_match", dict(projects=[0])),
        ("project1_match", dict(projects=[1])),
        ("locale_match", dict(locales=[0])),
        ("locale_and_project_match", dict(locales=[0], projects=[0])),
        ("locales_and_projects_match", dict(projects=[1, 2], locales=[0, 1])),
        ("priority_match", dict(priority=3)),
        ("priority_true_match", dict(priority=True)),
        ("priority_false_match", dict(priority=False)),
        ("path_no_match", dict(path="NOPATHSHERE")),
        ("path_match", dict(path=11)),
        ("slug_no_match", dict(slug="NOSLUGSHERE")),
        ("slug_exact", dict(slug=23)),
        ("slug_contains", dict(slug="factorytag7")),
    )
)


@pytest.fixture(params=_tag_kwargs)
def tag_test_kwargs(request, tag_matrix):
    """This is a parametrized fixture that provides a range of possible
    **kwargs for testing the TagsTool against tags in the `tag_matrix`
    fixture.

    If a parameter values for `path` is an `int` its mangled to the
    `path` of the `resource` (in the site_matrix) with the corresponding
    index.

    If a `slug` is an `int` its likewise mangled to the `tag`.`slug` with
    a corresponding index.

    `projects` and `locales` are similarly mangled to the corresponding
    projects/locales in the  site_matrix.

    Parameters that are suffixed with `_match` expect at least 1 result
    to be returned.

    Parameters suffixed with `_exact` expect exactly 1 result.

    Parameters suffixed with `_contains` expect more than 1 result.

    Finally, parameters suffixed with `_no_match` expect 0 results.
    """

    kwargs = _tag_kwargs.get(request.param).copy()
    if kwargs.get("path"):
        if isinstance(kwargs["path"], int):
            kwargs["path"] = tag_matrix["resources"][kwargs["path"]].path
    if kwargs.get("slug"):
        if isinstance(kwargs["slug"], int):
            kwargs["slug"] = tag_matrix["tags"][kwargs["slug"]].slug
    for k in ["projects", "locales"]:
        if kwargs.get(k):
            kwargs[k] = [tag_matrix[k][i] for i in kwargs[k]]
    return request.param, kwargs


_tag_data_init_kwargs = OrderedDict(
    (
        (
            "no_args",
            dict(
                annotations=None,
                groupby=None,
                locales=None,
                path=None,
                priority=None,
                projects=None,
                slug=None,
            ),
        ),
        (
            "args",
            dict(
                annotations=1,
                groupby=2,
                locales=3,
                path=4,
                priority=5,
                projects=6,
                slug=7,
            ),
        ),
    )
)


@pytest.fixture(params=_tag_data_init_kwargs)
def tag_data_init_kwargs(request):
    """This is a parametrized fixture that provides 2 sets
    of possible **kwargs to instantiate the TagsDataTools with

    The first set of kwargs, are all set to `None` and the
    second contain numeric values for testing against
    """

    return _tag_data_init_kwargs.get(request.param).copy()


_tag_init_kwargs = OrderedDict(
    (
        (
            "no_args",
            dict(locales=None, path=None, priority=None, projects=None, slug=None),
        ),
        ("args", dict(locales=1, path=2, priority=3, projects=4, slug=5)),
    )
)


@pytest.fixture(params=_tag_init_kwargs)
def tag_init_kwargs(request):
    """This is a parametrized fixture that provides 2 sets
    of possible **kwargs to instantiate the TagsTool with

    The first set of kwargs, are all set to `None` and the
    second contain numeric values for testing against
    """

    return _tag_init_kwargs.get(request.param).copy()
