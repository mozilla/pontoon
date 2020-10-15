from django.conf.urls import url

from . import views


urlpatterns = [
    url(
        r"^batch-edit-translations/",
        views.batch_edit_translations,
        name="pontoon.batch.edit.translations",
    ),
]
