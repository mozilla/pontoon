from unittest.mock import MagicMock, patch, PropertyMock

import pytest

from django.db.models import QuerySet

from pontoon.base.models import TranslatedResource
from pontoon.tags.utils import TagsStatsTool


def test_util_tags_stats_tool(tag_data_init_kwargs):
    # tests instantiation of stats tool
    kwargs = tag_data_init_kwargs
    stats_tool = TagsStatsTool(**kwargs)
    for k, v in kwargs.items():
        assert getattr(stats_tool, k) == v
    assert stats_tool.tr_manager == TranslatedResource.objects


def test_util_tags_stats_tool_annotations():
    # tests annotations can be overridden
    stats_tool = TagsStatsTool()
    assert stats_tool.get_annotations() == stats_tool.default_annotations

    anno = dict(foo="foo0", bar="bar0")
    stats_tool = TagsStatsTool(annotations=anno)
    assert stats_tool.get_annotations() != stats_tool.default_annotations
    assert stats_tool.get_annotations() != anno
    anno.update(stats_tool.default_annotations)
    assert stats_tool.get_annotations() == anno


@patch("pontoon.tags.utils.TagsStatsTool.get_data")
def test_util_tags_stats_tool_data(data_mock):
    # tests coalescing and caching of data
    stats_tool = TagsStatsTool()
    data_mock.return_value = (1, 2, 3)
    result = stats_tool.data
    assert result == [1, 2, 3]
    assert data_mock.called
    data_mock.reset_mock()
    data_mock.return_value = (4, 5, 6)
    result = stats_tool.data
    assert not data_mock.called
    assert result == [1, 2, 3]
    del stats_tool.__dict__["data"]
    result = stats_tool.data
    assert data_mock.called
    assert result == [4, 5, 6]


@patch(
    "pontoon.tags.utils.TagsStatsTool.data", new_callable=PropertyMock,
)
def test_util_tags_stats_tool_len(data_pmock):
    # tests len(stats) is taken from data
    stats_tool = TagsStatsTool()
    data_pmock.return_value = [7, 23]
    result = len(stats_tool)
    assert data_pmock.called
    assert result == 2


@patch("pontoon.tags.utils.TagsStatsTool.data", new_callable=PropertyMock)
def test_util_tags_stats_tool_iter(data_pmock):
    # tests iter(stats) iterates the data
    stats_tool = TagsStatsTool()
    data_pmock.return_value = [7, 23]
    result = list(stats_tool)
    assert data_pmock.called
    assert result == [7, 23]


def test_util_tags_stats_tool_filters():
    # tests stats tool has expected filters
    stats_tool = TagsStatsTool()
    assert stats_tool.filters == [
        getattr(stats_tool, "filter_%s" % f) for f in stats_tool.filter_methods
    ]


@patch(
    "pontoon.tags.utils.TagsStatsTool.tr_manager", new_callable=PropertyMock,
)
@patch("pontoon.tags.utils.TagsStatsTool.filter_tag")
@patch("pontoon.tags.utils.TagsStatsTool.filter_projects")
@patch("pontoon.tags.utils.TagsStatsTool.filter_locales")
@patch("pontoon.tags.utils.TagsStatsTool.filter_path")
def test_util_tags_stats_tool_fitered_data(
    m_path, m_locales, m_proj, m_tag, trs_mock,
):
    # tests all filter functions are called when filtering data
    # and that they are called with the result of previous

    stats_tool = TagsStatsTool()
    m = m_tag, m_proj, m_locales, m_path

    # mock trs for translated_resources.all()
    _m = MagicMock()
    _m.all.return_value = 0
    trs_mock.return_value = _m

    for i, _m in enumerate(m):
        if i >= len(m) - 1:
            _m.return_value = 23
        else:
            _m.return_value = i

    # get the filtered_data
    result = stats_tool.filtered_data
    assert result == 23
    for i, _m in enumerate(m):
        assert _m.called
        if i > 0:
            assert _m.call_args[0][0] == i - 1


@pytest.mark.django_db
def test_util_tags_stats_tool_get_data_empty(calculate_tags, assert_tags):
    # tests stats tool and test calculation doesnt break if there is no data
    stats_tool = TagsStatsTool()
    data = stats_tool.get_data()
    assert isinstance(data, QuerySet)
    assert list(data) == []
    assert_tags(
        calculate_tags(), data,
    )


@pytest.mark.django_db
def test_util_tags_stats_tool_get_data_matrix(
    tag_matrix, calculate_tags, assert_tags, tag_test_kwargs,
):
    # for different parametrized kwargs, tests that the calculated stat data
    # matches expectations from long-hand calculation
    name, kwargs = tag_test_kwargs
    stats_tool = TagsStatsTool(**kwargs)
    data = stats_tool.get_data()
    assert isinstance(data, QuerySet)
    _tags = calculate_tags(**kwargs)
    assert_tags(_tags, data)

    if name.endswith("_exact"):
        assert len(data) == 1
    elif name.endswith("_no_match"):
        assert len(data) == 0
    elif name.endswith("_match"):
        assert len(data) > 0
    elif name.endswith("_contains"):
        assert 1 < len(data) < len(tag_matrix["tags"])
    elif name == "empty":
        pass
    else:
        raise ValueError("Unsupported assertion type: {}".format(name))

    if name.startswith("slug_") and "slug" in kwargs:
        for result in data:
            assert kwargs["slug"] in result["slug"]


@pytest.mark.django_db
def test_util_tags_stats_tool_groupby_locale(
    tag_matrix, calculate_tags, assert_tags, tag_test_kwargs,
):
    name, kwargs = tag_test_kwargs

    # this is only used with slug set to a unique slug, and doesnt work
    # correctly without
    if name == "slug_contains" or not kwargs.get("slug"):
        kwargs["slug"] = tag_matrix["tags"][0].slug

    stats_tool = TagsStatsTool(groupby="locale", **kwargs)
    data = stats_tool.get_data()
    # assert isinstance(data, QuerySet)
    exp = calculate_tags(groupby="locale", **kwargs)
    data = stats_tool.coalesce(data)
    assert len(data) == len(exp)
    for locale in data:
        locale_exp = exp[locale["locale"]]
        assert locale_exp["total_strings"] == locale["total_strings"]
        assert locale_exp["fuzzy_strings"] == locale["fuzzy_strings"]
        assert locale_exp["approved_strings"] == locale["approved_strings"]
