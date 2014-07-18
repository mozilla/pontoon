from django.contrib import admin
from pontoon.base.models import (
    UserProfile,
    Locale,
    Project,
    Subpage,
    Resource,
    Entity,
    Translation,
)

admin.site.register(UserProfile)
admin.site.register(Locale)
admin.site.register(Project)
admin.site.register(Subpage)
admin.site.register(Resource)
admin.site.register(Entity)
admin.site.register(Translation)
