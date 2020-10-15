from django.conf.urls import url

from pontoon.projects import views as projects_views
from pontoon.teams import views as teams_views

from . import views

urlpatterns = [
    # Localization page
    url(
        r"^(?P<code>[A-Za-z0-9\-\@\.]+)/(?P<slug>[\w-]+)/$",
        views.localization,
        name="pontoon.localizations.localization",
    ),
    # Localization tags
    url(
        r"^(?P<code>[A-Za-z0-9\-\@\.]+)/(?P<slug>[\w-]+)/tags/$",
        views.localization,
        name="pontoon.localizations.tags",
    ),
    # Localization contributors
    url(
        r"^(?P<code>[A-Za-z0-9\-\@\.]+)/(?P<slug>[\w-]+)/contributors/$",
        views.localization,
        name="pontoon.localizations.contributors",
    ),
    # Project info
    url(
        r"^(?P<code>[A-Za-z0-9\-\@\.]+)/(?P<slug>[\w-]+)/project-info/$",
        views.localization,
        name="pontoon.localizations.project-info",
    ),
    # Team info
    url(
        r"^(?P<code>[A-Za-z0-9\-\@\.]+)/(?P<slug>[\w-]+)/team-info/$",
        views.localization,
        name="pontoon.localizations.team-info",
    ),
    # AJAX view: Localization resources
    url(
        r"^(?P<code>[A-Za-z0-9\-\@\.]+)/(?P<slug>[\w-]+)/ajax/$",
        views.ajax_resources,
        name="pontoon.localizations.ajax.resources",
    ),
    # AJAX view: Localization tags
    url(
        r"^(?P<code>[A-Za-z0-9\-\@\.]+)/(?P<slug>[\w-]+)/ajax/tags/$",
        views.ajax_tags,
        name="pontoon.localizations.ajax.tags",
    ),
    # AJAX view: Localization contributors
    url(
        r"^(?P<code>[A-Za-z0-9\-\@\.]+)/(?P<slug>[\w-]+)/ajax/contributors/$",
        views.LocalizationContributorsView.as_view(),
        name="pontoon.localizations.ajax.contributors",
    ),
    # AJAX view: Project info
    url(
        r"^[A-Za-z0-9\-\@\.]+/(?P<slug>[\w-]+)/ajax/project-info/$",
        projects_views.ajax_info,
        name="pontoon.localizations.ajax.project-info",
    ),
    # AJAX view: Team info
    url(
        r"^(?P<locale>[A-Za-z0-9\-\@\.]+)/[\w-]+/ajax/team-info/$",
        teams_views.ajax_info,
        name="pontoon.localizations.ajax.team-info",
    ),
]
