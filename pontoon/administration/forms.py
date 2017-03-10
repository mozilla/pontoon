from django import forms
from django.contrib.auth.models import Group
from django.forms.models import inlineformset_factory

from pontoon.base.models import Project, Repository, Subpage, ExternalResource


class ContactChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.email


class ProjectForm(forms.ModelForm):
    # Group not created until data migration executes
    project_managers, _ = Group.objects.get_or_create(name="project_managers")
    contact_queryset = project_managers.user_set.order_by('email')
    contact = ContactChoiceField(contact_queryset, required=False)

    class Meta:
        model = Project
        fields = ('name', 'slug', 'locales', 'can_be_requested',
                  'url', 'width', 'links', 'info', 'admin_notes',
                  'deadline', 'priority', 'disabled')


SubpageInlineFormSet = inlineformset_factory(
    Project, Subpage,
    extra=1,
    fields=('project', 'name', 'url')
)


RepositoryInlineFormSet = inlineformset_factory(
    Project, Repository,
    extra=0,
    min_num=1,
    validate_min=True,
    fields=('type', 'url', 'branch', 'website', 'source_repo', 'permalink_prefix'),
)


class ExternalResourceInlineForm(forms.ModelForm):
    class Meta:
        model = ExternalResource
        widgets = {
            'name': forms.TextInput(attrs={
                'list': 'external-resource-types',
                'title': 'Use down arrow to reveal a list of possible values'
            }),
        }
        fields = ('project', 'name', 'url')


ExternalResourceInlineFormSet = inlineformset_factory(
    Project, ExternalResource,
    form=ExternalResourceInlineForm,
    extra=1
)
