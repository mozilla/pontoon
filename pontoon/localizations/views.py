from __future__ import division

import math

from django.db.models import Q
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.views.generic.detail import DetailView

from pontoon.base.models import Locale, Project, ProjectLocale, TranslatedResource
from pontoon.base.utils import require_AJAX
from pontoon.contributors.views import ContributorsMixin


def localization(request, code, slug):
    """Locale-project overview."""
    locale = get_object_or_404(Locale, code=code)
    project = get_object_or_404(Project.objects.available(), slug=slug)
    project_locale = get_object_or_404(ProjectLocale, locale=locale, project=project)

    resource_count = len(locale.parts_stats(project)) - 1

    return render(request, 'localizations/localization.html', {
        'locale': locale,
        'project': project,
        'project_locale': project_locale,
        'resource_count': resource_count,
    })


@require_AJAX
def ajax_resources(request, code, slug):
    """Resources tab."""
    locale = get_object_or_404(Locale, code=code)
    project = get_object_or_404(
        Project.objects.available().prefetch_related('subpage_set'),
        slug=slug
    )

    # Amend the parts dict with latest activity info.
    translatedresources_qs = (
        TranslatedResource.objects
        .filter(resource__project=project, locale=locale)
        .prefetch_related('resource', 'latest_translation__user')
    )

    if not len(translatedresources_qs):
        raise Http404

    pages = {}
    for page in project.subpage_set.all():
        latest_page_translatedresource = None
        page_translatedresources_qs = (
            TranslatedResource.objects
            .filter(resource__in=page.resources.all(), locale=locale)
            .prefetch_related('resource', 'latest_translation__user')
        )

        for page_translatedresource in page_translatedresources_qs:
            latest = (
                latest_page_translatedresource.latest_translation
                if latest_page_translatedresource
                else None
            )
            if (
                latest is None or
                (
                    page_translatedresource.latest_translation.latest_activity['date'] >
                    latest.latest_activity['date']
                )
            ):
                latest_page_translatedresource = page_translatedresource

        pages[page.name] = latest_page_translatedresource

    translatedresources = {s.resource.path: s for s in translatedresources_qs}
    translatedresources = dict(translatedresources.items() + pages.items())
    parts = locale.parts_stats(project)

    for part in parts:
        translatedresource = translatedresources.get(part['title'], None)
        if translatedresource and translatedresource.latest_translation:
            part['latest_activity'] = translatedresource.latest_translation.latest_activity
        else:
            part['latest_activity'] = None

        part['chart'] = {
            'translated_strings': part['translated_strings'],
            'fuzzy_strings': part['fuzzy_strings'],
            'total_strings': part['resource__total_strings'],
            'approved_strings': part['approved_strings'],
            'approved_share': round(
                part['approved_strings'] / part['resource__total_strings'] * 100
            ),
            'translated_share': round(
                part['translated_strings'] / part['resource__total_strings'] * 100
            ),
            'fuzzy_share': round(part['fuzzy_strings'] / part['resource__total_strings'] * 100),
            'approved_percent': int(
                math.floor(part['approved_strings'] / part['resource__total_strings'] * 100)
            ),
        }

    return render(request, 'localizations/includes/resources.html', {
        'locale': locale,
        'project': project,
        'resources': parts,
    })


class LocalizationContributorsView(ContributorsMixin, DetailView):
    """
    Renders view of contributors for the localization.
    """
    template_name = 'localizations/includes/contributors.html'

    def get_object(self):
        return get_object_or_404(
            ProjectLocale,
            locale__code=self.kwargs['code'],
            project__slug=self.kwargs['slug']
        )

    def get_context_object_name(self, obj):
        return 'projectlocale'

    def contributors_filter(self, **kwargs):
        return Q(
            entity__resource__project=self.object.project,
            locale=self.object.locale
        )
