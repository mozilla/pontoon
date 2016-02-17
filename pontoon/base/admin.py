from django.contrib import admin
from django.contrib.auth.models import User, Group

from pontoon.base.models import (
    UserProfile,
    Locale,
    Project,
    Subpage,
    Resource,
    Entity,
    Translation,
    Stats,
)

admin.site.register(UserProfile)
admin.site.register(User)
admin.site.register(Group)

admin.site.register(Locale)
admin.site.register(Project)
admin.site.register(Subpage)
admin.site.register(Resource)
admin.site.register(Entity)
admin.site.register(Translation)
admin.site.register(Stats)
