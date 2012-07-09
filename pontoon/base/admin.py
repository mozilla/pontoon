from pontoon.base.models import UserProfile, Locale, Project, Entity, Translation
from django.contrib import admin

admin.site.register(UserProfile)
admin.site.register(Locale)
admin.site.register(Project)
admin.site.register(Entity)
admin.site.register(Translation)
