from . import views
from django.urls import path


urlpatterns = [
    # Homepage
    path("", views.homepage, name="pontoon.homepage"),
]
