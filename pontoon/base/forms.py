import os

import bleach

from django import forms
from django.conf import settings

from pontoon.base.models import (
    Locale,
    ProjectLocale,
    User,
    UserProfile
)
from pontoon.sync.formats import SUPPORTED_FORMAT_PARSERS


class HtmlField(forms.CharField):
    widget = forms.Textarea

    def clean(self, value):
        value = super(HtmlField, self).clean(value)
        value = bleach.clean(
            value, strip=True,
            tags=settings.ALLOWED_TAGS, attributes=settings.ALLOWED_ATTRIBUTES
        )
        return value


class NoTabStopCharField(forms.CharField):
    widget = forms.TextInput(attrs={'tabindex': '-1'})


class NoTabStopFileField(forms.FileField):
    widget = forms.FileInput(attrs={'tabindex': '-1'})


class DownloadFileForm(forms.Form):
    slug = NoTabStopCharField()
    code = NoTabStopCharField()
    part = NoTabStopCharField()


class UploadFileForm(DownloadFileForm):
    uploadfile = NoTabStopFileField()

    def clean(self):
        cleaned_data = super(UploadFileForm, self).clean()
        part = cleaned_data.get("part")
        uploadfile = cleaned_data.get("uploadfile")

        if uploadfile:
            limit = 5000

            # File size validation
            if uploadfile.size > limit * 1000:
                current = round(uploadfile.size / 1000)
                message = (
                    'Upload failed. Keep filesize under {limit} kB. Your upload: {current} kB.'
                    .format(limit=limit, current=current)
                )
                raise forms.ValidationError(message)

            # File format validation
            if part:
                file_extension = os.path.splitext(uploadfile.name)[1].lower()
                part_extension = os.path.splitext(part)[1].lower()

                # For now, skip if uploading file while using subpages
                if part_extension in SUPPORTED_FORMAT_PARSERS.keys() and part_extension != file_extension:
                    message = (
                        'Upload failed. File format not supported. Use {supported}.'
                        .format(supported=part_extension)
                    )
                    raise forms.ValidationError(message)


class UserPermissionGroupForm(object):
    def assign_users_to_groups(self, group_name, users):
        """
        Clear group membership and assign a set of users to a given group of users.
        """
        group = getattr(self.instance, '{}_group'.format(group_name))
        group.user_set.clear()
        if users:
            group.user_set.add(*users)


class LocalePermsForm(forms.ModelForm, UserPermissionGroupForm):
    translators = forms.ModelMultipleChoiceField(queryset=User.objects.all(), required=False)
    managers = forms.ModelMultipleChoiceField(queryset=User.objects.all(), required=False)

    class Meta:
        model = Locale
        fields = ('translators', 'managers')

    def save(self, *args, **kwargs):
        self.assign_users_to_groups('translators', self.cleaned_data.get('translators', []))
        self.assign_users_to_groups('managers', self.cleaned_data.get('managers', []))


class ProjectLocalePermsForm(forms.ModelForm, UserPermissionGroupForm):
    translators = forms.ModelMultipleChoiceField(queryset=User.objects.all(), required=False)

    class Meta:
        model = ProjectLocale
        fields = ('translators', 'has_custom_translators')

    def save(self, *args, **kwargs):
        super(ProjectLocalePermsForm, self).save(*args, **kwargs)
        self.assign_users_to_groups('translators', self.cleaned_data.get('translators', []))


class ProjectLocaleFormSet(forms.models.BaseModelFormSet):
    """
    Formset will update only existing objects and won't allow to create new-ones.
    """

    @property
    def errors_dict(self):
        errors = {}
        for form in self:
            if form.errors:
                errors[form.instance.pk] = form.errors
        return errors

    def save(self, commit=True):
        self.new_objects = []
        if commit:
            for form in self:
                if form.instance.pk and form.cleaned_data.get('has_custom_translators'):
                    form.save()

            # We have to cleanup projects from translators
            without_translators = (
                form.instance.pk for form in self
                if form.instance.pk and not form.cleaned_data.get('has_custom_translators')
            )

            if not without_translators:
                return

            ProjectLocale.objects.filter(
                pk__in=without_translators
            ).update(has_custom_translators=False)

            User.groups.through.objects.filter(
                group__projectlocales__pk__in=without_translators
            ).delete()


ProjectLocalePermsFormsSet = forms.modelformset_factory(
    ProjectLocale,
    ProjectLocalePermsForm,
    formset=ProjectLocaleFormSet,
)


class UserFirstNameForm(forms.ModelForm):
    """
    Form is responsible for saving user's name.
    """
    first_name = forms.RegexField(regex='^[^<>"\'&]+$', max_length=30, strip=True)

    class Meta:
        model = User
        fields = ('first_name',)


class UserCustomHomepageForm(forms.ModelForm):
    """
    Form is responsible for saving custom home page.
    """
    class Meta:
        model = UserProfile
        fields = ('custom_homepage',)

    def __init__(self, *args, **kwargs):
        super(UserCustomHomepageForm, self).__init__(*args, **kwargs)
        all_locales = list(Locale.objects.all().values_list('code', 'name'))

        self.fields['custom_homepage'] = forms.ChoiceField(choices=[
            ('', 'Default homepage')
        ] + all_locales, required=False)


class UserLocalesOrderForm(forms.ModelForm):
    """
    Form is responsible for saving preferred locales of contributor.
    """
    class Meta:
        model = UserProfile
        fields = ('locales_order',)
