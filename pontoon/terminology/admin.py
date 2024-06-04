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
        "do_not_translate",
        "forbidden",
    )
    list_editable = (
        "status",
        "part_of_speech",
        "case_sensitive",
        "do_not_translate",
        "forbidden",
    )
    raw_id_fields = ("entity",)

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        obj.save()

    def get_fields(self, request, obj=None):
        fields = super().get_fields(request, obj)
        if obj is None:
            fields.remove("created_by")
            fields.remove("entity")
        return fields


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
