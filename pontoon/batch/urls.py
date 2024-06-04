from . import views
from django.urls import path


urlpatterns = [
    path(
        "batch-edit-translations/",
        views.batch_edit_translations,
        name="pontoon.batch.edit.translations",
    ),
]
