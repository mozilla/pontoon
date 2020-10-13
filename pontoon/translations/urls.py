from django.conf.urls import url

from . import views


urlpatterns = [
    url(r"^create/$", views.create_translation, name="pontoon.translations.create",),
    url(r"^delete/$", views.delete_translation, name="pontoon.translations.delete",),
    url(r"^approve/$", views.approve_translation, name="pontoon.translations.approve",),
    url(
        r"^unapprove/$",
        views.unapprove_translation,
        name="pontoon.translations.unapprove",
    ),
    url(r"^reject/$", views.reject_translation, name="pontoon.translations.reject",),
    url(
        r"^unreject/$",
        views.unreject_translation,
        name="pontoon.translations.unreject",
    ),
]
