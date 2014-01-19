import requests

from django.conf import settings
from django.contrib.auth.models import User, Permission
from django.db import models
from django.db.models.signals import post_save
from django.forms import ModelForm

class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)

    # Other fields here
    transifex_username = models.CharField(max_length=40)
    transifex_password = models.CharField(max_length=128)
    svn_username = models.CharField(max_length=40)
    svn_password = models.CharField(max_length=128)

# For every newly created user
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

        # Grant permission to Mozilla localizers
        url = "https://mozillians.org/api/v1/users/"
        payload = {
            "app_name": "pontoon",
            "app_key": settings.MOZILLIANS_API_KEY,
            "groups": "l10n",
            "format": "json",
            "limit": 1000, # By default, limited to 20
            "is_vouched": True
        }

        import commonware
        log = commonware.log.getLogger('pontoon')

        log.debug(instance.email)
        try:
            r = requests.get(url, params=payload)
            email = instance.email
            for l in r.json()["objects"]:
                if email == l["email"]:
                    can_localize = Permission.objects.get(codename="can_localize")
                    instance.user_permissions.add(can_localize)
                    log.debug("Permission can_localize set.")

                    # Fallback if profile does not allow accessing data
                    instance.first_name = l.get("full_name", email)
                    instance.save()
                    break;
        except Exception:
            pass

post_save.connect(create_user_profile, sender=User)

class Locale(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=128)

    def __unicode__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=128, unique=True)
    url = models.URLField("URL", unique=True)
    locales = models.ManyToManyField(Locale)

    # Repositories
    REPOSITORY_TYPE_CHOICES = (
        ('file', 'File'),
        ('hg', 'HG'),
        ('svn', 'SVN'),
        ('transifex', 'Transifex'),
    )
    repository_type = models.CharField("Type", max_length=20, blank=False, default='File', choices=REPOSITORY_TYPE_CHOICES)
    repository = models.URLField("URL", blank=True)
    repository_path = models.TextField(blank=True)
    transifex_project = models.CharField("Project", max_length=128, blank=True)
    transifex_resource = models.CharField("Resource", max_length=128, blank=True)

    # Format
    FORMAT_CHOICES = (
        ('po', 'po'),
        ('properties', 'properties'),
        ('ini', 'ini'),
        ('lang', 'lang'),
    )
    format = models.CharField("Format", max_length=20, blank=True, choices=FORMAT_CHOICES)

    # Campaign info
    info_brief = models.TextField("Campaign Brief", blank=True)
    info_locales = models.TextField("Intended Locales and Regions", blank=True)
    info_audience = models.TextField("Audience, Reach, and Impact", blank=True)
    info_metrics = models.TextField("Success Metrics", blank=True)

    # User interface
    external = models.BooleanField("Open project website in external window insted of iframe")
    links = models.BooleanField("Keep links on the project website clickable")

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
    comment = models.TextField(blank=True)
    key = models.TextField(blank=True) # Needed for webL10n
    source = models.TextField(blank=True) # Needed for webL10n

    def __unicode__(self):
        return self.string

class Translation(models.Model):
    entity = models.ForeignKey(Entity)
    locale = models.ForeignKey(Locale)
    string = models.TextField()
    author = models.CharField(max_length=128)
    date = models.DateTimeField()

    def __unicode__(self):
        return self.string

class ProjectForm(ModelForm):
    class Meta:
        model = Project

    def clean(self):
        cleaned_data = super(ProjectForm, self).clean()
        repository = cleaned_data.get("repository")
        repository_type = cleaned_data.get("repository_type")
        transifex_project = cleaned_data.get("transifex_project")
        transifex_resource = cleaned_data.get("transifex_resource")

        if repository_type == 'Transifex':
            if not transifex_project:
                self._errors["repository"] = self.error_class([u"You need to provide Transifex project and resource."])
                del cleaned_data["transifex_resource"]

            if not transifex_resource:
                self._errors["repository"] = self.error_class([u"You need to provide Transifex project and resource."])
                del cleaned_data["transifex_project"]

        elif not repository:
            self._errors["repository"] = self.error_class([u"You need to provide a valid URL."])

        return cleaned_data
