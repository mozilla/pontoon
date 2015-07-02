from django.contrib import admin
from pontoon.base.models import (
    UserProfile,
    CLDR_Plurals,
    Locale,
    Project,
    Subpage,
    Resource,
    Entity,
    Translation,
    Stats,
)

admin.site.register(UserProfile)
admin.site.register(CLDR_Plurals)
admin.site.register(Locale)
admin.site.register(Project)
admin.site.register(Subpage)
admin.site.register(Resource)
admin.site.register(Entity)
admin.site.register(Translation)
admin.site.register(Stats)
