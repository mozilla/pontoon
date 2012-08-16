from django.db import models
from django.contrib.auth.models import User
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

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

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
    svn = models.URLField("SVN", unique=True)
    transifex_project = models.CharField(max_length=128)
    transifex_resource = models.CharField(max_length=128)

    # Campaign info
    info_brief = models.TextField("Campaign Brief")
    info_locales = models.TextField("Intended Locales and Regions")
    info_audience = models.TextField("Audience, Reach, and Impact")
    info_metrics = models.TextField("Success Metrics")

    class Meta:
        permissions = (
            ("can_manage", "Can manage projects"),
        )

    def __unicode__(self):
        return self.name

class Subpage(models.Model):
    project = models.ForeignKey(Project)
    name = models.CharField(max_length=128)
    url = models.URLField()

    def __unicode__(self):
        return self.name

class Entity(models.Model):
    project = models.ForeignKey(Project)
    string = models.TextField()
    comment = models.TextField()

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
