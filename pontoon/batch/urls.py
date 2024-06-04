from django.urls import path

from . import views


urlpatterns = [
    path(
        "batch-edit-translations/",
        views.batch_edit_translations,
        name="pontoon.batch.edit.translations",
    ),
]
