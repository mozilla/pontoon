from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)

    # Other fields here
    transifex_username = models.CharField(max_length=20)
    transifex_password = models.CharField(max_length=128)
    svn_username = models.CharField(max_length=20)
    svn_password = models.CharField(max_length=128)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)

class Locale(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    def __unicode__(self):
        return self.name

class Project(models.Model):
    name = models.CharField(max_length=100, unique=True)
    url = models.URLField(unique=True)
    locales = models.ManyToManyField(Locale)

    class Meta:
        permissions = (
            ("can_manage", "Can manage projects"),
        )

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
    author = models.CharField(max_length=100)
    date = models.DateTimeField()

    def __unicode__(self):
        return self.string
