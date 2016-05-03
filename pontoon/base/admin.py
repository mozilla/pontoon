from django.contrib import admin
from django.contrib.auth.models import User, Group
from pontoon.base import models


class UserAdmin(admin.ModelAdmin):
    search_fields = ['email', 'first_name']

admin.site.register(Group)
admin.site.register(User, UserAdmin)

admin.site.register(models.Entity)
admin.site.register(models.Locale)
admin.site.register(models.Project)
admin.site.register(models.Repository)
admin.site.register(models.Resource)
admin.site.register(models.Subpage)
admin.site.register(models.TranslatedResource)
admin.site.register(models.Translation)
admin.site.register(models.UserProfile)
