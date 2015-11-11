from django.conf.urls import patterns, url
from django.views.generic import RedirectView

import views

urlpatterns = patterns(
    '',

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

    # List all active localization teams
    url(r'^teams/$',
        views.locales,
        name='pontoon.teams'),

    # Redirect to a team page
    url(r'^teams/(?P<locale>[A-Za-z0-9\-\@\.]+)/$',
        RedirectView.as_view(url="/%(locale)s/", permanent=True)),

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

    # AJAX: Get project details
    url(r'^projects/(?P<slug>[\w-]+)/details/$', views.get_project_details,
        name='pontoon.project.details'),

    # List team contributors
    url(r'^(?P<code>[A-Za-z0-9\-\@\.]+)/contributors/$',
        views.LocaleContributorsView.as_view(),
        name='pontoon.locale.contributors'),

    # Manage team
    url(r'^(?P<locale>[A-Za-z0-9\-\@\.]+)/manage/$',
        views.locale_manage,
        name='pontoon.locale.manage'),

    # Translate project
    url(r'^(?P<locale>[A-Za-z0-9\-\@\.]+)/(?P<slug>[\w-]+)/(?P<part>.+)/$',
        views.translate,
        name='pontoon.translate'),

    # Locale-project dashboard
    url(r'^(?P<locale>[A-Za-z0-9\-\@\.]+)/(?P<slug>[\w-]+)/$',
        views.locale_project,
        name='pontoon.locale.project'),

    # List contributors
    url(r'^contributors/$',
        views.ContributorsView.as_view(),
        name='pontoon.contributors'),

    # Contributor profile
    url(r'^contributors/(?P<email>[\w.%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,4})/$',
        views.contributor,
        name='pontoon.contributor'),

    # Current user profile
    url(r'^profile/$',
        views.profile,
        name='pontoon.profile'),

    # Terminology Search
    url(r'^terminology/$',
        views.search,
        name='pontoon.search'),

    # Legacy: Redirect to /terminology
    url(r'^search/$',
        RedirectView.as_view(pattern_name='pontoon.search', permanent=True)),

    # AJAX
    url(r'^get-entities/', views.entities,
        name='pontoon.entities'),
    url(r'^update/', views.update_translation,
        name='pontoon.update'),
    url(r'^get-history/', views.get_translation_history,
        name='pontoon.get_history'),
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
    url(r'^transvision-aurora/$', views.transvision_aurora,
        name='pontoon.transvision_aurora'),
    url(r'^transvision-gaia/$', views.transvision_gaia,
        name='pontoon.transvision_gaia'),
    url(r'^transvision-mozilla-org/$', views.transvision_mozilla_org,
        name='pontoon.transvision_mozilla_org'),
    url(r'^other-locales/', views.get_translations_from_other_locales,
        name='pontoon.other_locales'),
    url(r'^download/', views.download,
        name='pontoon.download'),
    url(r'^quality-checks-switch/', views.quality_checks_switch,
        name='pontoon.quality_checks_switch'),
    url(r'^request-locale/', views.request_locale,
        name='pontoon.request_locale'),
    url(r'^save-user-name/', views.save_user_name,
        name='pontoon.save_user_name'),
    url(r'^transifex/$', views.save_to_transifex,
        name='pontoon.transifex'),
    url(r'^csrf/$', views.get_csrf,
        name='pontoon.csrf'),

    # Team page: Must be at the end
    url(r'^(?P<locale>[A-Za-z0-9\-\@\.]+)/$',
        views.locale,
        name='pontoon.locale'),

)
