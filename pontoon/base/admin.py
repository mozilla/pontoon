from django.contrib import admin
from pontoon.base.models import (
    UserProfile,
    Locale,
    Project,
    Subpage,
    Resource,
    TranslatedResource,
    Entity,
    Translation,
)

admin.site.register(UserProfile)
admin.site.register(Locale)
admin.site.register(Project)
admin.site.register(Subpage)
admin.site.register(Resource)
admin.site.register(TranslatedResource)
admin.site.register(Entity)
admin.site.register(Translation)
