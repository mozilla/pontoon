
import pytest

from mock import MagicMock, PropertyMock, patch

from django import forms

from pontoon.base.models import Resource
from pontoon.tags.admin.forms import LinkTagResourcesAdminForm


@pytest.mark.django_db
def test_form_project_tag_resources(client, project0, tag0):
    # tests instantiation of TagResourcesForm

    with pytest.raises(KeyError):
        # needs a project
        LinkTagResourcesAdminForm()

    form = LinkTagResourcesAdminForm(project=project0)
    assert not form.is_valid()
    assert form.project == project0
    assert form.fields.keys() == ['tag', 'type', 'data', 'search']
    assert (
        list(form.fields['data'].choices)
        == list(Resource.objects.filter(
            project=project0).values_list('path', 'pk')))


@pytest.mark.django_db
def test_form_project_tag_resources_submit_bad(project0):
    # tests the various reasons a form is not valid

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
@patch('pontoon.tags.admin.forms.LinkTagResourcesAdminForm.'
       '_clean_paths_for_select')
def test_form_project_tag_resources_submit(paths_mock, project0, tag0):
    # tests submitting with no data - which should return a list of paths
    # _clean_paths_for_select
    paths_mock.return_value = 23

    # test assoc form submit
    form = LinkTagResourcesAdminForm(
        project=project0,
        data=dict(type='assoc', tag=tag0.slug))
    assert form.is_valid()
    assert (
        form.cleaned_data
        == {'action': None,
            'data': 23,
            'search': u'',
            'tag': u'tag0',
            'type': u'assoc'})

    # test nonassoc form submit
    form = LinkTagResourcesAdminForm(
        project=project0,
        data=dict(type='nonassoc', tag=tag0.slug))
    assert form.is_valid()
    assert (
        form.cleaned_data
        == {'action': None,
            'data': 23,
            'search': u'',
            'tag': u'tag0',
            'type': u'nonassoc'})


@pytest.mark.django_db
@patch('pontoon.tags.admin.forms.LinkTagResourcesAdminForm.'
       '_clean_paths_for_submit')
def test_form_project_tag_resources_submit_paths(paths_mock, project0, tag0):
    # tests submitting with data, which should validate using
    # _clean_paths_for_submit
    paths_mock.return_value = 113

    # test assoc form submit
    form = LinkTagResourcesAdminForm(
        project=project0,
        data=dict(
            type='assoc',
            tag=tag0.slug,
            data=list(tag0.resources.values_list('path', flat=True))))
    assert form.is_valid()
    assert (
        form.cleaned_data
        == {'action': form.tag_tool.unlink_resources,
            'data': 113,
            'search': u'',
            'tag': u'tag0',
            'type': u'assoc'})

    # test nonassoc form submit
    form = LinkTagResourcesAdminForm(
        project=project0,
        data=dict(
            type='nonassoc',
            tag=tag0.slug,
            data=list(tag0.resources.values_list('path', flat=True))))
    assert form.is_valid()
    assert (
        form.cleaned_data
        == {'action': form.tag_tool.link_resources,
            'data': 113,
            'search': u'',
            'tag': u'tag0',
            'type': u'nonassoc'})


@pytest.mark.django_db
@patch('pontoon.tags.admin.forms.LinkTagResourcesAdminForm.'
       '_clean_paths_for_submit')
def test_form_project_tag_resources_submit_paths_bad(paths_mock, project0,
                                                     tag0):
    # tests that the form should not be valid if _clean_paths_for_submit
    # raises a ValidationError
    paths_mock.side_effect = forms.ValidationError('Ooops!')

    form = LinkTagResourcesAdminForm(
        project=project0,
        data=dict(
            type='assoc',
            tag=tag0.slug,
            data=list(tag0.resources.values_list('path', flat=True))))
    assert not form.is_valid()
    assert form.errors == {'data': [u'Ooops!']}


@pytest.mark.django_db
def test_form_project_tag_resources_action_type(project0):
    # tests that the form displays the correct action_type
    # name for error messages

    form = LinkTagResourcesAdminForm(project=project0)
    form.cleaned_data = dict()
    assert not form.action_type
    form.cleaned_data = dict(type='assoc')
    assert form.action_type == 'unlink'
    form.cleaned_data = dict(type='nonassoc')
    assert form.action_type == 'link'


@pytest.mark.django_db
@patch('pontoon.tags.admin.forms.TagsTool')
def test_form_project_tag_resources_tag_tool(paths_mock, project0):
    # tests form.tag_tool is created correctly
    paths_mock.configure_mock(
        **{'return_value.get.return_value': 23})

    form = LinkTagResourcesAdminForm(project=project0)
    form.cleaned_data = dict(tag='FOO')
    assert form.tag_tool == 23
    assert (
        list(paths_mock.call_args)
        == [(), {'projects': [project0]}])
    assert (
        list(paths_mock.return_value.get.call_args)
        == [('FOO',), {}])


@pytest.mark.django_db
@patch('pontoon.tags.admin.forms.LinkTagResourcesAdminForm.tag_tool',
       new_callable=PropertyMock())
def test_form_project_tag_resources_resources(tag_mock, project0):
    # tests that linked/linkable resources are correctly found
    tag_mock.configure_mock(
        **{'linkable_resources': 7,
           'linked_resources': 23})

    form = LinkTagResourcesAdminForm(project=project0)
    form.cleaned_data = dict(type='nonassoc')
    assert form.resources == 7
    form.cleaned_data = dict(type='assoc')
    assert form.resources == 23


@pytest.mark.django_db
@patch('pontoon.tags.admin.forms.LinkTagResourcesAdminForm.resources',
       new_callable=PropertyMock())
@patch('pontoon.tags.admin.forms.glob_to_regex')
def test_form_project_tag_resources_paths_for_select(glob_mock, resources_mock,
                                                     project0):
    # tests that selected paths are correct filtered
    resources_mock.configure_mock(
        **{'filter.return_value.values_list.return_value': 23,
           'values_list.return_value': 17})
    glob_mock.return_value = 7

    form = LinkTagResourcesAdminForm(project=project0)

    # no search filter set, all resources returned
    form.cleaned_data = dict(search='')
    assert form._clean_paths_for_select() == 17
    assert not resources_mock.filter.called
    assert not glob_mock.called

    # search set, resources filtered
    form.cleaned_data = dict(search='*')
    assert form._clean_paths_for_select() == 23
    assert (
        list(resources_mock.filter.call_args)
        == [(), {'path__regex': 7}])
    assert (
        list(glob_mock.call_args)
        == [('*',), {}])


@pytest.mark.django_db
@patch('pontoon.tags.admin.forms.LinkTagResourcesAdminForm.resources',
       new_callable=PropertyMock())
def test_form_project_tag_resources_paths_for_submit(resources_mock, project0):
    # tests that submitted paths are correctly validated
    resources_mock.filter.return_value = [1, 2, 3]

    form = LinkTagResourcesAdminForm(project=project0)
    form.cleaned_data = dict(action=True, type='assoc', data=[4, 5, 6])

    # _clean_paths_for_submit returns filtered resources
    assert form._clean_paths_for_submit() == [1, 2, 3]

    # filter was called with list of paths
    assert (
        list(resources_mock.filter.call_args)
        == [(), {'path__in': [4, 5, 6]}])

    # the number of paths is different so validation fails
    resources_mock.filter.return_value = [1, 2]

    with pytest.raises(forms.ValidationError):
        form._clean_paths_for_submit()


@pytest.mark.django_db
@patch('pontoon.tags.admin.forms.LinkTagResourcesAdminForm.'
       '_clean_paths_for_select')
def test_form_project_tag_resources_save(paths_mock, project0):
    # tests the form.save method
    #
    # if cleaned_data['action'] was set this will
    # first call the associated un/link action with the paths
    #
    # it returns a list of selectable paths after any action is
    # complete

    # return a generator to ensure conversion to a list
    paths_mock.return_value = (x for x in [23])

    form = LinkTagResourcesAdminForm(project=project0)

    # call with generator to ensure conversion to list
    form.cleaned_data = dict(action=None, data=(x for x in [7]))

    # no action, returns list(cleaned_data['data'])
    assert form.save() == [7]

    # data was not generated again after validation
    assert not paths_mock.called

    # action is set, and will be called with paths
    action = MagicMock()
    form.cleaned_data['action'] = action
    assert form.save() == [23]
    assert (
        list(action.call_args)
        == [(form.cleaned_data['data'], ), {}])
