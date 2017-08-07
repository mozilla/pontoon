from django.contrib import admin

from pontoon.terminology import models


class TermTranslationInline(admin.StackedInline):
    model = models.TermTranslation
    max_num = 1
    can_delete = False


class TermAdmin(admin.ModelAdmin):
    exclude = ('entities',)
    inlines = (TermTranslationInline,)


admin.site.register(models.Term, TermAdmin)
