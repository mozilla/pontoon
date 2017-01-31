from django.forms import ModelForm
from django.forms.models import inlineformset_factory

from pontoon.base.models import Project, Repository, Subpage


class ProjectForm(ModelForm):
    class Meta:
        model = Project
        fields = ('name', 'slug', 'locales',
                  'info_brief', 'url', 'width',
                  'links', 'disabled')


SubpageInlineFormSet = inlineformset_factory(
    Project, Subpage,
    extra=1,
    fields=('project', 'name', 'url')
)


RepositoryInlineFormSet = inlineformset_factory(
    Project, Repository,
    extra=1,
    fields=('type', 'url', 'branch', 'source_repo', 'permalink_prefix'),
)
