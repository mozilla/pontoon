
from django import forms
from django.utils.functional import cached_property

from pontoon.base.models import Resource
from pontoon.base.utils import glob_to_regex
from pontoon.tags.utils import TagsTool


class LinkTagResourcesAdminForm(forms.Form):
    tag = forms.CharField(required=True)
    type = forms.ChoiceField(
        choices=[
            (x, x.capitalize())
            for x
            in ['assoc', 'nonassoc']])
    data = forms.MultipleChoiceField(choices=[], required=False)
    search = forms.CharField(required=False)

    def __init__(self, *args, **kwargs):
        self.project = kwargs.pop('project')
        super(LinkTagResourcesAdminForm, self).__init__(*args, **kwargs)
        # we cant filter any further at this stage as we dont know the
        # action yet
        self.fields['data'].choices = Resource.objects.filter(
            project=self.project).values_list('path', 'pk')

    @cached_property
    def tag_tool(self):
        return TagsTool(
            projects=[self.project]).get(self.cleaned_data['tag'])

    def clean(self):
        cleaned_data = super(LinkTagResourcesAdminForm, self).clean()
        if self.errors:
            return
        try:
            tag_tool = self.tag_tool
        except IndexError:
            return self.add_error(
                'tag',
                'Unrecognized tag: %s'
                % cleaned_data['tag'])
        if self.cleaned_data['data']:
            try:
                self.cleaned_data['data'] = self._clean_paths_for_submit()
            except forms.ValidationError as e:
                return self.add_error('data', e)
            self.cleaned_data["action"] = (
                tag_tool.link_resources
                if self.cleaned_data['type'] == 'nonassoc'
                else tag_tool.unlink_resources)
        else:
            # get a list of paths that can be used in the form
            self.cleaned_data['data'] = self._clean_paths_for_select()
            self.cleaned_data['action'] = None

    @property
    def action_type(self):
        return (
            self.cleaned_data.get('action') is not None
            and ('link'
                 if self.cleaned_data['type'] == 'nonassoc'
                 else 'unlink'))

    @property
    def resources(self):
        return (
            self.tag_tool.linkable_resources
            if self.cleaned_data['type'] == 'nonassoc'
            else self.tag_tool.linked_resources)

    def _clean_paths_for_select(self):
        qs = self.resources
        if self.cleaned_data['search']:
            qs = qs.filter(
                path__regex=glob_to_regex(
                    self.cleaned_data['search']))
        return qs.values_list('path')

    def _clean_paths_for_submit(self):
        paths = list(
            self.resources.filter(path__in=self.cleaned_data['data']))
        if len(paths) != len(self.cleaned_data['data']):
            # the length of the paths requested to be added/removed
            # should be the same as the validated paths length.
            raise forms.ValidationError(
                'Unable to %s the resources requested'
                % self.action_type)
        return paths

    def save(self):
        if self.cleaned_data['action'] is None:
            return list(self.cleaned_data['data'])
        self.cleaned_data['action'](self.cleaned_data['data'])
        return list(self._clean_paths_for_select())
