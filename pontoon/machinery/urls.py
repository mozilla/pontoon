from django.conf.urls import url
from django.views.generic import RedirectView

import views

urlpatterns = [
    # Machinery Metasearch
    url(r'^machinery/$',
        views.machinery,
        name='pontoon.machinery'),

    # Legacy: Redirect to /machinery
    url(r'^search/$',
        RedirectView.as_view(pattern_name='pontoon.machinery', permanent=True)),
    url(r'^terminology/$',
        RedirectView.as_view(pattern_name='pontoon.machinery', permanent=True)),

    # AJAX
    url(r'^translation-memory/$', views.translation_memory,
        name='pontoon.translation_memory'),
    url(r'^machine-translation/$', views.machine_translation,
        name='pontoon.machine_translation'),
    url(r'^microsoft-terminology/$', views.microsoft_terminology,
        name='pontoon.microsoft_terminology'),
    url(r'^amagama/$', views.amagama,
        name='pontoon.amagama'),
    url(r'^transvision/$', views.transvision,
        name='pontoon.transvision'),
]
