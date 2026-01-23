from urllib.parse import urlencode

import requests

from requests.exceptions import RequestException

from django.http import Http404, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.urls import reverse

from pontoon.base.models.entity import Entity
from pontoon.base.models.locale import Locale
from pontoon.base.models.project import Project
from pontoon.base.utils import get_project_locale_from_request, require_AJAX
from pontoon.settings.base import SITE_URL


def create_api_url(
    search,
    project,
    locale,
    search_identifiers,
    search_match_case,
    search_match_whole_word,
    page=None,
):
    search_match_case = search_match_case == "true"
    search_identifiers = search_identifiers == "true"
    search_match_whole_word = search_match_whole_word == "true"

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
        if value is not None and value != "" and value is not False
    }

    if page:
        query_params["page"] = page

    return f"{SITE_URL}/api/v2/search/translations/?{urlencode(query_params)}"


def entity_search(request):
    """Get corresponding entity given entity."""

    search = request.GET.get("search")
    locale = request.GET.get("locale")
    project = request.GET.get("project")
    search_identifiers = request.GET.get("search_identifiers")
    search_match_case = request.GET.get("search_match_case")
    search_match_whole_word = request.GET.get("search_match_whole_word")

    projects = list(
        Project.objects.visible()
        .visible_for(request.user)
        .prefetch_related(
            "contact",
        )
    )

    default_project = Project(name="All Projects", slug="all-projects")
    projects.insert(0, default_project)

    if not project or not Project.objects.filter(slug=project).exists():
        preferred_project = default_project
        project = None
    else:
        preferred_project = Project.objects.get(slug=project)

    locales = list(Locale.objects.available())

    if not locale or not Locale.objects.filter(code=locale).exists():
        locale = get_project_locale_from_request(request, Locale.objects) or "en-GB"

    preferred_locale = Locale.objects.get(code=locale)

    if not search:
        return render(
            request,
            "search/search.html",
            {
                "entities": [],
                "search": "",
                "locales": locales,
                "projects": projects,
                "preferred_locale": preferred_locale,
                "preferred_project": preferred_project,
                "search_identifiers_enabled": search_identifiers == "true",
                "match_case_enabled": search_match_case == "true",
                "match_whole_word_enabled": search_match_whole_word == "true",
            },
        )

    api_url = create_api_url(
        search,
        project,
        locale,
        search_identifiers,
        search_match_case,
        search_match_whole_word,
    )

    try:
        response = requests.get(api_url)
        response.raise_for_status()
    except RequestException:
        raise Http404

    if response.status_code == 200:
        entities = response.json()["results"]
        has_more = response.json()["next"]
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
                "search_identifiers_enabled": search_identifiers == "true",
                "match_case_enabled": search_match_case == "true",
                "match_whole_word_enabled": search_match_whole_word == "true",
                "has_more": has_more,
            },
        )

    else:
        raise Http404


@require_AJAX
def more_entities(request):
    page = request.GET.get("page")

    search = request.GET.get("search")
    locale = request.GET.get("locale")
    project = request.GET.get("project")
    search_identifiers = request.GET.get("search_identifiers")
    search_match_case = request.GET.get("search_match_case")
    search_match_whole_word = request.GET.get("search_match_whole_word")

    if not locale or not Locale.objects.filter(code=locale).exists():
        locale = get_project_locale_from_request(request, Locale.objects) or "en-GB"

    api_url = create_api_url(
        search,
        project,
        locale,
        search_identifiers,
        search_match_case,
        search_match_whole_word,
        page=page,
    )

    try:
        response = requests.get(api_url)
        response.raise_for_status()
    except RequestException:
        raise Http404

    if response.status_code == 200:
        entities = response.json()["results"]
        has_more = response.json()["next"] is not None

        html = render_to_string(
            "search/widgets/entity_list.html",
            {
                "entities": entities,
                "preferred_locale": Locale.objects.get(code=locale),
                "search": search,
                "search_identifiers_enabled": search_identifiers == "true",
                "match_case_enabled": search_match_case == "true",
                "match_whole_word_enabled": search_match_whole_word == "true",
            },
        )
        return JsonResponse(
            {"html": html, "has_more": has_more},
        )

    return JsonResponse({"error": "No results found."}, status=404)


def entity(request, pk):
    """Get corresponding entity given entity id."""
    api_url = f"{SITE_URL}/api/v2/entities/{pk}/?include_translations=True"
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
                "entity": entity,
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
