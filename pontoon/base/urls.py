from django.conf.urls import url
from django.views.generic import RedirectView, TemplateView

import views

urlpatterns = [
    # Home
    url(r'^$', views.home, name='pontoon.home'),

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

    # AJAX: Get locale-project pages/paths with stats
    url(r'^(?P<locale>[A-Za-z0-9\-\@\.]+)/(?P<slug>[\w-]+)/parts/$',
        views.locale_project_parts,
        name='pontoon.locale.project.parts'),

    # Translate project
    url(r'^(?P<locale>[A-Za-z0-9\-\@\.]+)/(?P<slug>[\w-]+)/(?P<part>.+)/$',
        views.translate,
        name='pontoon.translate'),

    # AJAX
    url(r'^get-entities/', views.entities,
        name='pontoon.entities'),
    url(r'^batch-edit-translations/', views.batch_edit_translations,
        name='pontoon.batch.edit.translations'),
    url(r'^update/', views.update_translation,
        name='pontoon.update'),
    url(r'^get-history/', views.get_translation_history,
        name='pontoon.get_history'),
    url(r'^unapprove-translation/', views.unapprove_translation,
        name='pontoon.unapprove_translation'),
    url(r'^delete-translation/', views.delete_translation,
        name='pontoon.delete_translation'),
    url(r'^other-locales/', views.get_translations_from_other_locales,
        name='pontoon.other_locales'),
    url(r'^download/', views.download,
        name='pontoon.download'),
    url(r'^upload/', views.upload,
        name='pontoon.upload'),
]
