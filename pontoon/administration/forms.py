from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.forms.models import inlineformset_factory

from pontoon.base.forms import HtmlField
from pontoon.base.models import (
    Entity,
    ExternalResource,
    Locale,
    Project,
    Repository,
    Resource,
)
from pontoon.tags.models import Tag


class ContactChoiceField(forms.ModelChoiceField):
    def label_from_instance(self, obj):
        return obj.email


class ProjectForm(forms.ModelForm):
    contact = ContactChoiceField(None, required=False)
    info = HtmlField(required=False)
    locales_readonly = forms.ModelMultipleChoiceField(
        queryset=Locale.objects.all(),
        required=False,
    )
    locales = forms.ModelMultipleChoiceField(
        queryset=Locale.objects.all(),
        required=False,
    )
    locales_pretranslate = forms.ModelMultipleChoiceField(
        queryset=Locale.objects.all(),
        required=False,
    )

    def clean(self):
        cleaned_data = super().clean()
        locales_readonly = cleaned_data.get("locales_readonly")
        locales = cleaned_data.get("locales")
        if not (locales or locales_readonly):
            raise ValidationError("At least one locale must be selected.")

    class Meta:
        model = Project
        fields = (
            "name",
            "slug",
            "locales",
            "data_source",
            "can_be_requested",
            "configuration_file",
            "info",
            "admin_notes",
            "deadline",
            "priority",
            "contact",
            "disabled",
            "sync_disabled",
            "tags_enabled",
            "pretranslation_enabled",
            "visibility",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["contact"].queryset = User.objects.filter(
            groups__name="project_managers"
        ).order_by("email")


RepositoryInlineFormSet = inlineformset_factory(
    Project,
    Repository,
    extra=1,
    min_num=0,
    validate_min=True,
    fields=("type", "url", "branch", "website", "source_repo"),
)


class ExternalResourceInlineForm(forms.ModelForm):
    class Meta:
        model = ExternalResource
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "list": "external-resource-types",
                    "title": "Use down arrow to reveal a list of possible values",
                }
            ),
        }
        fields = ("project", "name", "url")


ExternalResourceInlineFormSet = inlineformset_factory(
    Project, ExternalResource, form=ExternalResourceInlineForm, extra=1
)


EntityFormSet = forms.modelformset_factory(
    Entity,
    fields=("string", "comment", "obsolete"),
    extra=1,
)


class TagInlineForm(forms.ModelForm):
    resources = forms.ModelMultipleChoiceField(
        queryset=Resource.objects.none(),
        required=False,
    )

    class Meta:
        model = Tag
        fields = ("project", "slug", "name", "priority", "resources")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # If the project instance is available, filter resources for this project
        if kwargs.get("instance") and kwargs["instance"].project:
            project = kwargs["instance"].project
            self.fields["resources"].queryset = Resource.objects.filter(
                project=project
            ).select_related()


TagInlineFormSet = inlineformset_factory(Project, Tag, form=TagInlineForm, extra=1)
