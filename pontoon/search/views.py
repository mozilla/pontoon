from urllib.parse import urlencode

import requests

from requests.exceptions import RequestException

from django.db.models import Prefetch
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from pontoon.base import utils
from pontoon.base.models.entity import Entity
from pontoon.base.models.locale import Locale
from pontoon.base.models.project import Project
from pontoon.base.models.project_locale import ProjectLocale
from pontoon.settings.base import SITE_URL


def translation_search(request):
    """Get corresponding entity given entity."""

    search = request.GET.get("search")
    locale = request.GET.get("locale")
    project = request.GET.get("project")
    search_identifiers = request.GET.get("search_identifiers")
    search_match_case = request.GET.get("search_match_case")
    search_match_whole_word = request.GET.get("search_match_whole_word")

    search_match_case = search_match_case == "true" or False
    search_identifiers = search_identifiers == "true" or False
    search_match_whole_word = search_match_whole_word == "true" or False

    projects = list(
        Project.objects.visible()
        .visible_for(request.user)
        .prefetch_related(
            Prefetch(
                "project_locale",
                queryset=ProjectLocale.objects.visible().select_related("locale"),
                to_attr="fetched_project_locales",
            ),
            "contact",
            "tags",
        )
    )

    default_project = Project(name="All Projects", slug="all-projects")
    projects.insert(0, default_project)

    if not project or not Project.objects.filter(slug=project).exists():
        preferred_project = default_project
        project = None
    else:
        preferred_project = Project.objects.get(slug=project)

    locales = list(
        Locale.objects.prefetch_related(
            Prefetch(
                "project_locale",
                queryset=ProjectLocale.objects.visible().select_related("project"),
                to_attr="fetched_project_locales",
            )
        ).distinct()
    )

    if not locale or not Locale.objects.filter(code=locale).exists():
        locale = (
            utils.get_project_locale_from_request(request, Locale.objects) or "en-GB"
        )

    preferred_locale = Locale.objects.get(code=locale)

    if not search:
        return render(
            request,
            "search/search.html",
            {
                "search": "",
                "locales": locales,
                "projects": projects,
                "preferred_locale": preferred_locale,
                "preferred_project": preferred_project,
                "search_identifiers_enabled": search_identifiers,
                "match_case_enabled": search_match_case,
                "match_whole_word_enabled": search_match_whole_word,
            },
        )

    query_params = {
        "text": search,
        "project": project,
        "locale": locale,
        "search_identifiers": search_identifiers,
        "search_match_case": search_match_case,
        "search_match_whole_word": search_match_whole_word,
    }

    query_params = {
        key: value
        for key, value in query_params.items()
        if value is not None and not False
    }

    api_url = f"{SITE_URL}/api/v2/search/translations/?{urlencode(query_params)}"

    try:
        response = requests.get(api_url)
        response.raise_for_status()
    except RequestException:
        raise Http404

    if response.status_code == 200:
        entities = response.json()["results"]
        return render(
            request,
            "search/search.html",
            {
                "entities": entities,
                "search": search,
                "locales": locales,
                "projects": projects,
                "preferred_locale": preferred_locale,
                "preferred_project": preferred_project,
                "search_identifiers_enabled": search_identifiers,
                "match_case_enabled": search_match_case,
                "match_whole_word_enabled": search_match_whole_word,
            },
        )

    else:
        raise Http404


def entity(request, pk):
    """Get corresponding entity given entity id."""
    api_url = f"{SITE_URL}/api/v2/entities/{pk}/?include_translations"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
    except RequestException:
        raise Http404

    if response.status_code == 200:
        entity = response.json()
        return render(
            request,
            "search/entity.html",
            {
                "entity": entity.get("entity", []),
                "project": entity.get("project", []),
                "resource": entity.get("resource", []),
                "translations": entity.get("translations", []),
            },
        )
    else:
        raise Http404


def entity_alternate(request, project, resource, entity):
    """Get corresponding entity given entity."""

    entity = get_object_or_404(
        Entity,
        resource__project__slug=project,
        resource__path=resource,
        key__overlap=[entity],
    )

    return redirect(reverse("pontoon.entity", kwargs={"pk": entity.pk}))
