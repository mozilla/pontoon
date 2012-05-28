from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)

    # Other fields here
    transifex_username = models.CharField(max_length=20)
    transifex_password = models.CharField(max_length=128)

User.profile = property(lambda u: UserProfile.objects.get_or_create(user=u)[0])
