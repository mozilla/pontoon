from django import forms
from django.contrib.auth.models import User
from django.forms.models import inlineformset_factory

from pontoon.base.models import Project, Repository, Subpage


class ContactChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.email


class ProjectForm(forms.ModelForm):
    contact_queryset = User.objects.exclude(email='').order_by('email')
    l10n_contact = ContactChoiceField(contact_queryset, required=False)
    project_contact = ContactChoiceField(contact_queryset, required=False)

    class Meta:
        model = Project
        fields = ('name', 'slug', 'locales', 'can_be_requested',
                  'url', 'width', 'links', 'info', 'deadline', 'priority',
                  'preview_url', 'project_url', 'disabled')


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
