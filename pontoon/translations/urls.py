from django.urls import path

from . import views


urlpatterns = [
    path("create/", views.create_translation, name="pontoon.translations.create",),
    path("delete/", views.delete_translation, name="pontoon.translations.delete",),
    path("approve/", views.approve_translation, name="pontoon.translations.approve",),
    path(
        "unapprove/",
        views.unapprove_translation,
        name="pontoon.translations.unapprove",
    ),
    path("reject/", views.reject_translation, name="pontoon.translations.reject",),
    path(
        "unreject/", views.unreject_translation, name="pontoon.translations.unreject",
    ),
]
