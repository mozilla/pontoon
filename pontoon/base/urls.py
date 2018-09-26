from django.conf.urls import url
from django.views.generic import RedirectView, TemplateView

import views

urlpatterns = [
    # Terms
    url(r'^terms/$',
        TemplateView.as_view(template_name='terms.html'),
        name='pontoon.terms'),

    # TRANSLATE URLs

    # Legacy: Translate project's page
    url(r'^locale/(?P<locale>[A-Za-z0-9\-\@\.]+)/project/(?P<slug>.+)' +
        '/page/(?P<page>.+)/$',
        RedirectView.as_view(url="/%(locale)s/%(slug)s/%(page)s/", permanent=True)),

    # Legacy: Translate project
    url(r'^locale/(?P<locale>[A-Za-z0-9\-\@\.]+)/project/(?P<slug>.+)/$',
        RedirectView.as_view(url="/%(locale)s/%(slug)s/", permanent=True)),

    # AJAX: Get locale details
    url(r'^teams/(?P<locale>[A-Za-z0-9\-\@\.]+)/projects/$',
        views.locale_projects,
        name='pontoon.locale.projects'),

    # AJAX: Get locale stats used in All Resources part
    url(r'^teams/(?P<locale>[A-Za-z0-9\-\@\.]+)/stats/$',
        views.locale_stats,
        name='pontoon.locale.stats'),

    # AJAX: Get locale-project pages/paths with stats
    url(r'^(?P<locale>[A-Za-z0-9\-\@\.]+)/(?P<slug>[\w-]+)/parts/$',
        views.locale_project_parts,
        name='pontoon.locale.project.parts'),

    # AJAX: Get authors and time range data
    url(r'^(?P<locale>[A-Za-z0-9\-\@\.]+)/(?P<slug>[\w-]+)/(?P<part>.+)/authors-and-time-range/$',
        views.authors_and_time_range,
        name='pontoon.authors.and.time.range'),

    # Locale-agnostic links
    url(r'^projects/(?P<slug>[\w-]+)/(?P<part>.+)/$',
        views.translate_locale_agnostic,
        name='pontoon.translate.locale.agnostic'),

    # Translate project
    url(r'^(?P<locale>[A-Za-z0-9\-\@\.]+)/(?P<slug>[\w-]+)/(?P<part>.+)/$',
        views.translate,
        name='pontoon.translate'),

    # Download translation memory
    url(r'^(?P<locale>[A-Za-z0-9\-\@\.]+)/(?P<slug>[\w-]+)/(?P<filename>.+)\.tmx$',
        views.download_translation_memory,
        name='pontoon.download_tmx'),

    # AJAX
    url(r'^get-entities/', views.entities,
        name='pontoon.entities'),
    url(r'^update/', views.update_translation,
        name='pontoon.update'),
    url(r'^perform-checks/', views.perform_checks,
        name='pontoon.perform.checks'),
    url(r'^get-history/', views.get_translation_history,
        name='pontoon.get_history'),
    url(r'^unapprove-translation/', views.unapprove_translation,
        name='pontoon.unapprove_translation'),
    url(r'^reject-translation/', views.reject_translation,
        name='pontoon.reject_translation'),
    url(r'^unreject-translation/', views.unreject_translation,
        name='pontoon.unreject_translation'),
    url(r'^other-locales/', views.get_translations_from_other_locales,
        name='pontoon.other_locales'),
    url(r'^download/', views.download,
        name='pontoon.download'),
    url(r'^upload/', views.upload,
        name='pontoon.upload'),

    url(
        r'^user-data/',
        views.user_data,
        name='pontoon.user_data'
    ),
]
