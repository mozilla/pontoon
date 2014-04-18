
import json

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.forms import ModelForm


class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)

    # Other fields here
    transifex_username = models.CharField(max_length=40, blank=True)
    transifex_password = models.CharField(max_length=128, blank=True)
    svn_username = models.CharField(max_length=40, blank=True)
    svn_password = models.CharField(max_length=128, blank=True)


# For every newly created user
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)


class Locale(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=128)
    nplurals = models.SmallIntegerField(null=True, blank=True)
    plural_rule = models.CharField(max_length=128, blank=True)

    def __unicode__(self):
        return self.name

    def stringify(self):
        return json.dumps({
            'code': self.code,
            'name': self.name,
            'nplurals': self.nplurals,
            'plural_rule': self.plural_rule,
        })


class Project(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(unique=True)
    locales = models.ManyToManyField(Locale)

    # Repositories
    REPOSITORY_TYPE_CHOICES = (
        ('file', 'File'),
        ('git', 'Git'),
        ('hg', 'HG'),
        ('svn', 'SVN'),
        ('transifex', 'Transifex'),
    )

    repository_type = models.CharField(
        "Type", max_length=20, blank=False, default='File',
        choices=REPOSITORY_TYPE_CHOICES)

    # URLField does not take git@github.com:user/project.git URLs
    repository_url = models.CharField("URL", max_length=2000, blank=True)

    # Includes source directory in one-locale repositories
    repository_path = models.TextField(blank=True)

    transifex_project = models.CharField(
        "Project", max_length=128, blank=True)
    transifex_resource = models.CharField(
        "Resource", max_length=128, blank=True)

    # Format
    FORMAT_CHOICES = (
        ('po', 'po'),
        ('properties', 'properties'),
        ('ini', 'ini'),
        ('lang', 'lang'),
    )
    format = models.CharField(
        "Format", max_length=20, blank=True, choices=FORMAT_CHOICES)

    # Project info
    info_brief = models.TextField("Project info", blank=True)

    # Website for in-place localization
    url = models.URLField("URL", blank=True)
    width = models.PositiveIntegerField(
        "Default website (iframe) width in pixels. If set, \
        sidebar will be opened by default.", null=True, blank=True)
    links = models.BooleanField(
        "Keep links on the project website clickable")

    class Meta:
        permissions = (
            ("can_manage", "Can manage projects"),
            ("can_localize", "Can localize projects"),
        )

    def __unicode__(self):
        return self.name


class Subpage(models.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=128)
    url = models.URLField("URL")

    def __unicode__(self):
        return self.name


class Entity(models.Model):
    project = models.ForeignKey(Project)
    string = models.TextField()
    string_plural = models.TextField(blank=True)
    comment = models.TextField(blank=True)
    key = models.TextField(blank=True)  # Needed for webL10n
    source = models.TextField(blank=True)

    def __unicode__(self):
        return self.string

    def serialize(self):
        try:
            source = eval(self.source)
        except SyntaxError:
            source = self.source

        return {
            'pk': self.pk,
            'original': self.string,
            'original_plural': self.string_plural,
            'comment': self.comment,
            'key': self.key,
            'source': source,
        }


class Translation(models.Model):
    entity = models.ForeignKey(Entity)
    locale = models.ForeignKey(Locale)
    user = models.ForeignKey(User, null=True, blank=True)
    string = models.TextField()
    # 0=zero, 1=one, 2=two, 3=few, 4=many, 5=other, null=no plural forms
    plural_form = models.SmallIntegerField(null=True, blank=True)
    date = models.DateTimeField()
    approved = models.BooleanField(default=False)
    fuzzy = models.BooleanField(default=False)

    def __unicode__(self):
        return self.string


class ProjectForm(ModelForm):
    class Meta:
        model = Project

    def clean(self):
        cleaned_data = super(ProjectForm, self).clean()
        repository_url = cleaned_data.get("repository_url")
        repository_type = cleaned_data.get("repository_type")
        transifex_project = cleaned_data.get("transifex_project")
        transifex_resource = cleaned_data.get("transifex_resource")

        if repository_type == 'Transifex':
            if not transifex_project:
                self._errors["repository_url"] = self.error_class(
                    [u"You need to provide Transifex project and resource."])
                del cleaned_data["transifex_resource"]

            if not transifex_resource:
                self._errors["repository_url"] = self.error_class(
                    [u"You need to provide Transifex project and resource."])
                del cleaned_data["transifex_project"]

        elif not repository_url:
            self._errors["repository_url"] = self.error_class(
                [u"You need to provide a valid URL."])

        return cleaned_data
