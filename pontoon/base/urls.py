from django.conf.urls import url
from django.views.generic import RedirectView, TemplateView

import views

urlpatterns = [
    # Home
    url(r'^$', views.home, name='pontoon.home'),

    # Legacy: Translate project's page
    url(r'^locale/(?P<locale>[A-Za-z0-9\-\@\.]+)/project/(?P<slug>.+)' +
        '/page/(?P<page>.+)/$',
        RedirectView.as_view(url="/%(locale)s/%(slug)s/%(page)s/", permanent=True)),

    # Legacy: Translate project
    url(r'^locale/(?P<locale>[A-Za-z0-9\-\@\.]+)/project/(?P<slug>.+)/$',
        RedirectView.as_view(url="/%(locale)s/%(slug)s/", permanent=True)),

    # Legacy: Redirect to /projects
    url(r'^project/$',
        RedirectView.as_view(url="/projects/", permanent=True)),

    # Legacy: Redirect to /projects/slug
    url(r'^project/(?P<slug>[\w-]+)/$',
        RedirectView.as_view(url="/projects/%(slug)s/", permanent=True)),

    # Legacy: Redirect to /contributors/email
    url(r'^contributor/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$',
        RedirectView.as_view(url="/contributors/%(email)s/", permanent=True)),

    # List contributors
    url(r'^contributors/$',
        views.ContributorsView.as_view(),
        name='pontoon.contributors'),

    # Contributor profile by email
    url(r'^contributors/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$',
        views.contributor_email,
        name='pontoon.contributor.email'),

    # Contributor timeline
    url(r'^contributors/(?P<username>[\w-]+)/timeline/$',
        views.contributor_timeline,
        name='pontoon.contributor.timeline'),

    # Contributor profile by username
    url(r'^contributors/(?P<username>[\w-]+)/$',
        views.contributor_username,
        name='pontoon.contributor.username'),

    # Current user profile
    url(r'^profile/$',
        views.profile,
        name='pontoon.profile'),

    # API: Toogle user profile attribute
    url(r'^api/v1/user/(?P<username>[\w-]+)/$',
        views.toggle_user_profile_attribute,
        name='pontoon.toggle_user_profile_attribute'),

    # List all active localization teams
    url(r'^teams/$',
        views.locales,
        name='pontoon.teams'),

    # Redirect to a team page
    url(r'^teams/(?P<locale>[A-Za-z0-9\-\@\.]+)/$',
        RedirectView.as_view(url="/%(locale)s/", permanent=True)),

    # AJAX: Get locale details
    url(r'^teams/(?P<locale>[A-Za-z0-9\-\@\.]+)/projects/$',
        views.locale_projects,
        name='pontoon.locale.projects'),

    # AJAX: Request projects to be added to locale
    url(r'^teams/(?P<locale>[A-Za-z0-9\-\@\.]+)/request/$',
        views.request_projects,
        name='pontoon.locale.request'),

    # List all imported projects
    url(r'^projects/$',
        views.projects,
        name='pontoon.projects'),

    # List project locales
    url(r'^projects/(?P<slug>[\w-]+)/$',
        views.project,
        name='pontoon.project'),

    # List project contributors
    url(r'^projects/(?P<slug>[\w-]+)/contributors/$',
        views.ProjectContributorsView.as_view(),
        name='pontoon.project.contributors'),

    # Sync project
    url(r'^projects/(?P<slug>[\w-]+)/sync/$',
        views.manually_sync_project,
        name='pontoon.project.sync'),

    # List team contributors
    url(r'^(?P<code>[A-Za-z0-9\-\@\.]+)/contributors/$',
        views.LocaleContributorsView.as_view(),
        name='pontoon.locale.contributors'),

    # Team permissions
    url(r'^(?P<locale>[A-Za-z0-9\-\@\.]+)/permissions/$',
        views.locale_permissions,
        name='pontoon.locale.permissions'),

    # Legacy url for the locale management panel.
    url(r'^(?P<locale>[A-Za-z0-9\-\@\.]+)/manage/$',
        RedirectView.as_view(url='/%(locale)s/permissions/', permanent=True),
        name='pontoon.locale.manage'),

    # AJAX: Request project to be added to locale
    url(r'^(?P<locale>[A-Za-z0-9\-\@\.]+)/(?P<slug>[\w-]+)/parts/$',
        views.locale_project_parts,
        name='pontoon.locale.project.parts'),

    # Translate project
    url(r'^(?P<locale>[A-Za-z0-9\-\@\.]+)/(?P<slug>[\w-]+)/(?P<part>.+)/$',
        views.translate,
        name='pontoon.translate'),

    # Locale-project dashboard
    url(r'^(?P<locale>[A-Za-z0-9\-\@\.]+)/(?P<slug>[\w-]+)/$',
        views.locale_project,
        name='pontoon.locale.project'),

    # Terminology Search
    url(r'^terminology/$',
        views.search,
        name='pontoon.search'),

    # Legacy: Redirect to /terminology
    url(r'^search/$',
        RedirectView.as_view(pattern_name='pontoon.search', permanent=True)),

    # Terms
    url(r'^terms/$',
        TemplateView.as_view(template_name='terms.html'),
        name='pontoon.terms'),

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
    url(r'^other-locales/', views.get_translations_from_other_locales,
        name='pontoon.other_locales'),
    url(r'^download/', views.download,
        name='pontoon.download'),
    url(r'^upload/', views.upload,
        name='pontoon.upload'),
    url(r'^save-user-name/', views.save_user_name,
        name='pontoon.save_user_name'),
    url(r'^csrf/$', views.get_csrf,
        name='pontoon.csrf'),
    url(r'^settings/', views.user_settings,
        name='pontoon.user_settings'),

    # Urls related to integration with Heroku
    url(r'^heroku-setup/', views.heroku_setup,
        name='pontoon.heroku_setup'),

    # Team page: Must be at the end
    url(r'^(?P<locale>[A-Za-z0-9\-\@\.]+)/$',
        views.locale,
        name='pontoon.locale'),

]
