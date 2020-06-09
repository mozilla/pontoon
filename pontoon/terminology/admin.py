from django.contrib import admin

from pontoon.terminology.models import Term, TermTranslation


class TermAdmin(admin.ModelAdmin):
    search_fields = [
        "text",
        "part_of_speech",
        "definition",
        "usage",
        "notes",
    ]
    list_display = (
        "text",
        "status",
        "part_of_speech",
        "definition",
        "usage",
        "notes",
        "case_sensitive",
        "exact_match",
        "do_not_translate",
        "forbidden",
    )
    list_editable = (
        "status",
        "part_of_speech",
        "case_sensitive",
        "exact_match",
        "do_not_translate",
        "forbidden",
    )
    raw_id_fields = ("entity",)


class TermTranslationAdmin(admin.ModelAdmin):
    search_fields = [
        "text",
    ]
    list_display = (
        "text",
        "term",
        "locale",
    )


admin.site.register(Term, TermAdmin)
admin.site.register(TermTranslation, TermTranslationAdmin)
