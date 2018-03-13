
from contextlib import nested

import pytest

from mock import MagicMock, PropertyMock, patch

from django import forms

from pontoon.base.models import Resource
from pontoon.tags.admin.forms import LinkTagResourcesAdminForm


@pytest.mark.django_db
def test_form_project_tag_resources(client, admin0, project0, tag0):

    with pytest.raises(KeyError):
        # needs a project
        LinkTagResourcesAdminForm()

    form = LinkTagResourcesAdminForm(project=project0)

    assert form.project == project0
    assert form.fields.keys() == ['tag', 'type', 'data', 'search']
    assert (
        list(form.fields['data'].choices)
        == list(Resource.objects.filter(
            project=project0).values_list('path', 'pk')))


@pytest.mark.django_db
def test_form_project_tag_resources_submit_bad(project0):
    form = LinkTagResourcesAdminForm(project=project0)
    assert not form.is_valid()

    form = LinkTagResourcesAdminForm(project=project0, data={})
    assert not form.is_valid()
    assert (
        form.errors
        == {'tag': [u'This field is required.'],
            'type': [u'This field is required.']})

    form = LinkTagResourcesAdminForm(
        project=project0,
        data=dict(type='foo'))
    assert not form.is_valid()
    assert (
        form.errors
        == {'tag': [u'This field is required.'],
            'type': [
                u'Select a valid choice. '
                u'foo is not one of the available choices.']})

    form = LinkTagResourcesAdminForm(
        project=project0,
        data=dict(type='assoc', tag='DOESNOTEXIST'))
    assert not form.is_valid()
    assert (
        form.errors
        == {'tag': [u'Unrecognized tag: DOESNOTEXIST']})


@pytest.mark.django_db
def test_form_project_tag_resources_submit(project0, tag0):
    form = LinkTagResourcesAdminForm(project=project0)
    assert not form.is_valid()

    form = LinkTagResourcesAdminForm(
        project=project0,
        data=dict(type='assoc', tag=tag0.slug))

    _patch_ctx = patch(
        'pontoon.tags.admin.forms.LinkTagResourcesAdminForm.'
        '_clean_paths_for_select')
    with _patch_ctx as m:
        m.return_value = 23
        assert form.is_valid()
        assert (
            form.cleaned_data
            == {'action': None,
                'data': 23,
                'search': u'',
                'tag': u'tag0',
                'type': u'assoc'})

    form = LinkTagResourcesAdminForm(
        project=project0,
        data=dict(type='nonassoc', tag=tag0.slug))

    with _patch_ctx as m:
        m.return_value = 23
        assert form.is_valid()
        assert (
            form.cleaned_data
            == {'action': None,
                'data': 23,
                'search': u'',
                'tag': u'tag0',
                'type': u'nonassoc'})


@pytest.mark.django_db
def test_form_project_tag_resources_submit_paths(project0, tag0):
    form = LinkTagResourcesAdminForm(project=project0)
    assert not form.is_valid()

    _patch_ctx = patch(
        'pontoon.tags.admin.forms.LinkTagResourcesAdminForm.'
        '_clean_paths_for_submit')

    form = LinkTagResourcesAdminForm(
        project=project0,
        data=dict(
            type='assoc',
            tag=tag0.slug,
            data=list(tag0.resources.values_list('path', flat=True))))
    with _patch_ctx as m:
        m.return_value = 113
        assert form.is_valid()
        assert (
            form.cleaned_data
            == {'action': form.tag_tool.unlink_resources,
                'data': 113,
                'search': u'',
                'tag': u'tag0',
                'type': u'assoc'})

    form = LinkTagResourcesAdminForm(
        project=project0,
        data=dict(
            type='nonassoc',
            tag=tag0.slug,
            data=list(tag0.resources.values_list('path', flat=True))))
    with _patch_ctx as m:
        m.return_value = 113
        assert form.is_valid()
        assert (
            form.cleaned_data
            == {'action': form.tag_tool.link_resources,
                'data': 113,
                'search': u'',
                'tag': u'tag0',
                'type': u'nonassoc'})


@pytest.mark.django_db
def test_form_project_tag_resources_submit_paths_bad(project0, tag0):
    form = LinkTagResourcesAdminForm(project=project0)
    assert not form.is_valid()

    form = LinkTagResourcesAdminForm(
        project=project0,
        data=dict(
            type='assoc',
            tag=tag0.slug,
            data=list(tag0.resources.values_list('path', flat=True))))

    _patch_ctx = patch(
        'pontoon.tags.admin.forms.LinkTagResourcesAdminForm.'
        '_clean_paths_for_submit')
    with _patch_ctx as m:
        m.side_effect = forms.ValidationError('Ooops!')
        assert not form.is_valid()
        assert form.errors == {'data': [u'Ooops!']}


@pytest.mark.django_db
def test_form_project_tag_resources_action_type(project0):
    form = LinkTagResourcesAdminForm(project=project0)
    form.cleaned_data = dict()
    assert form.action_type is False
    form.cleaned_data = dict(type='assoc')
    assert form.action_type is False
    form.cleaned_data = dict(type='assoc', action=1)
    assert form.action_type == 'unlink'
    form.cleaned_data = dict(type='nonassoc', action=1)
    assert form.action_type == 'link'


@pytest.mark.django_db
def test_form_project_tag_resources_tag_tool(project0):
    form = LinkTagResourcesAdminForm(project=project0)

    _patch_ctx = patch(
        'pontoon.tags.admin.forms.TagsTool')

    with _patch_ctx as m:
        get_m = MagicMock()
        get_m.get.return_value = 23
        m.return_value = get_m
        form.cleaned_data = dict(tag='FOO')
        assert form.tag_tool == 23
        assert (
            list(m.call_args)
            == [(), {'projects': [project0]}])
        assert (
            list(get_m.get.call_args)
            == [('FOO',), {}])


@pytest.mark.django_db
def test_form_project_tag_resources_resources(project0):
    form = LinkTagResourcesAdminForm(project=project0)

    _patch_ctx = patch(
        'pontoon.tags.admin.forms.LinkTagResourcesAdminForm.tag_tool',
        new_callable=PropertyMock())

    with _patch_ctx as p:
        type(p).linkable_resources = PropertyMock(return_value=7)
        type(p).linked_resources = PropertyMock(return_value=23)
        form.cleaned_data = dict(type='nonassoc')
        assert form.resources == 7
        form.cleaned_data = dict(type='assoc')
        assert form.resources == 23


@pytest.mark.django_db
def test_form_project_tag_resources_paths_for_select(project0):
    form = LinkTagResourcesAdminForm(project=project0)

    _patch_ctx = [
        patch(
            'pontoon.tags.admin.forms.LinkTagResourcesAdminForm.resources',
            new_callable=PropertyMock()),
        patch('pontoon.tags.admin.forms.glob_to_regex')]

    with nested(*_patch_ctx) as (p, m):
        filter_m = MagicMock()
        filter_m.values_list.return_value = 23
        p.filter.return_value = filter_m
        p.values_list.return_value = 17
        m.return_value = 7

        form.cleaned_data = dict(search='')
        assert form._clean_paths_for_select() == 17
        assert not p.filter.called
        assert not m.called

        form.cleaned_data = dict(search='*')
        assert form._clean_paths_for_select() == 23
        assert (
            list(p.filter.call_args)
            == [(), {'path__regex': 7}])
        assert (
            list(m.call_args)
            == [('*',), {}])


@pytest.mark.django_db
def test_form_project_tag_resources_paths_for_submit(project0):
    form = LinkTagResourcesAdminForm(project=project0)

    _patch_ctx = patch(
        'pontoon.tags.admin.forms.LinkTagResourcesAdminForm.resources',
        new_callable=PropertyMock())

    with _patch_ctx as p:
        p.filter.return_value = [1, 2, 3]
        form.cleaned_data = dict(action=True, type='assoc', data=[4, 5, 6])
        assert form._clean_paths_for_submit() == [1, 2, 3]
        assert (
            list(p.filter.call_args)
            == [(), {'path__in': [4, 5, 6]}])

        p.filter.return_value = [1, 2]

        with pytest.raises(forms.ValidationError):
            form._clean_paths_for_submit()


@pytest.mark.django_db
def test_form_project_tag_resources_save(project0):
    form = LinkTagResourcesAdminForm(project=project0)

    _patch_ctx = patch(
        'pontoon.tags.admin.forms.LinkTagResourcesAdminForm.'
        '_clean_paths_for_select')

    with _patch_ctx as m:
        m.return_value = (x for x in [23])
        form.cleaned_data = dict(action=None, data=(x for x in [7]))
        assert form.save() == [7]
        assert not m.called

        form.cleaned_data['action'] = MagicMock()
        assert form.save() == [23]
        assert (
            list(form.cleaned_data['action'].call_args)
            == [(form.cleaned_data['data'], ), {}])
