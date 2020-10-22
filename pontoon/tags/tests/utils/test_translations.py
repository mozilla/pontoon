from unittest.mock import MagicMock, patch

import pytest

from pontoon.base.models import Translation
from pontoon.tags.utils import TagsLatestTranslationsTool


def test_util_tags_stats_tool(tag_data_init_kwargs):
    # tests instantiation of translations tool
    kwargs = tag_data_init_kwargs
    tr_tool = TagsLatestTranslationsTool(**kwargs)
    for k, v in kwargs.items():
        assert getattr(tr_tool, k) == v


@pytest.mark.django_db
def test_util_tags_translation_tool_get_data(
    tag_matrix, calculate_tags_latest, tag_test_kwargs,
):
    # for different parametrized kwargs, tests that the calculated
    # latest data matches expectations from long-hand calculation
    name, kwargs = tag_test_kwargs

    # calculate expectations
    exp = calculate_tags_latest(**kwargs)

    # get the data, and coalesce to translations dictionary
    tr_tool = TagsLatestTranslationsTool(**kwargs)
    data = tr_tool.coalesce(tr_tool.get_data())

    # get a pk dictionary of all translations
    translations = Translation.objects.select_related("user").in_bulk()

    assert len(data) == len(exp)

    for k, (pk, date) in exp.items():
        assert data[k]["date"] == date
        assert data[k]["string"] == translations.get(pk).string

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


@patch("pontoon.tags.utils.TagsLatestTranslationsTool.get_data")
def test_util_tags_translation_tool_data(data_mock):
    # ensures latest translation data is coalesced and cached
    # correctly
    tr_tool = TagsLatestTranslationsTool()

    # set up mock return for get_data that can be used like
    # qs.iterator()
    data_m = [
        dict(entity__resource__tag="foo"),
        dict(entity__resource__tag="bar"),
    ]
    data_m2 = [dict(entity__resource__tag="baz")]
    iterator_m = MagicMock()
    iterator_m.iterator.return_value = data_m
    data_mock.return_value = iterator_m

    # get data from the tool
    result = tr_tool.data

    # we got back data from data_m coalesced to a dictionary
    # with the groupby fields as keys
    assert result == dict(foo=data_m[0], bar=data_m[1])
    assert iterator_m.iterator.called

    # lets reset the mock and change the return value
    iterator_m.reset_mock()
    iterator_m.iterator.return_value = data_m2

    # and get the data again
    result = tr_tool.data

    # which was cached, so nothing changed
    assert not iterator_m.iterator.called
    assert result == dict(foo=data_m[0], bar=data_m[1])

    # after deleting the cache...
    del tr_tool.__dict__["data"]

    # ...we get the new value
    result = tr_tool.data
    assert iterator_m.iterator.called
    assert result == dict(baz=data_m2[0])


@pytest.mark.django_db
def test_util_tags_translation_tool_groupby(
    tag_matrix, tag_test_kwargs, calculate_tags_latest, user_a, user_b,
):
    name, kwargs = tag_test_kwargs

    # hmm, translations have no users
    #  - set first 3rd to user_a, and second 3rd to user_b
    total = Translation.objects.count()
    first_third_users = Translation.objects.all()[: total / 3].values_list("pk")
    second_third_users = Translation.objects.all()[
        total / 3 : 2 * total / 3
    ].values_list("pk")
    (Translation.objects.filter(pk__in=first_third_users).update(user=user_a))
    (Translation.objects.filter(pk__in=second_third_users).update(user=user_b))

    # calculate expectations grouped by locale
    exp = calculate_tags_latest(groupby="locale", **kwargs)

    # calculate data from tool grouped by locale
    tr_tool = TagsLatestTranslationsTool(groupby="locale", **kwargs)
    data = tr_tool.coalesce(tr_tool.get_data())

    # get a pk dictionary of all translations
    translations = Translation.objects.select_related("user").in_bulk()

    assert len(data) == len(exp)

    for k, (pk, date) in exp.items():
        # check all of the expected values are correct for the
        # translation and user
        translation = translations.get(pk)
        assert data[k]["date"] == date
        assert data[k]["string"] == translation.string
        assert data[k]["approved_date"] == translation.approved_date
        user = translation.user
        if user:
            assert data[k]["user__email"] == user.email
            assert data[k]["user__first_name"] == user.first_name
        else:
            assert data[k]["user__email"] is None
            assert data[k]["user__first_name"] is None
