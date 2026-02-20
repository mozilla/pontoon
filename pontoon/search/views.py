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
from pontoon.base.utils import get_project_locale_from_request, parse_bool, require_AJAX
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


def search(request):
    """Render the search page with filters for searching entities."""
    locale_code = request.GET.get("locale")
    project_slug = request.GET.get("project")
    search_identifiers = parse_bool(request.GET.get("search_identifiers"))
    search_match_case = parse_bool(request.GET.get("search_match_case"))
    search_match_whole_word = parse_bool(request.GET.get("search_match_whole_word"))

    projects = list(
        Project.objects.visible()
        .visible_for(request.user)
        .prefetch_related(
            "contact",
        )
        .order_by("name")
    )

    default_project = Project(name="All Projects", slug="all-projects")
    projects.insert(0, default_project)

    project = (
        Project.objects.filter(slug=project_slug).first()
        if project_slug
        else default_project
    )

    locales = list(Locale.objects.visible())

    if (
        not locale_code
        or not Locale.objects.visible().filter(code=locale_code).exists()
    ):
        locale_code = (
            get_project_locale_from_request(request, Locale.objects.visible())
            or "en-GB"
        )

    locale = Locale.objects.get(code=locale_code)

    return render(
        request,
        "search/search.html",
        {
            "entities": [],
            "search": request.GET.get("search", ""),
            "locales": locales,
            "projects": projects,
            "locale": locale,
            "project": project,
            "search_identifiers_enabled": search_identifiers,
            "match_case_enabled": search_match_case,
            "match_whole_word_enabled": search_match_whole_word,
        },
    )


@require_AJAX
def search_results(request):
    try:
        pages = int(request.GET.get("pages", 1))
    except ValueError:
        pages = 1

    page = request.GET.get("page")
    search = request.GET.get("search")
    locale_code = request.GET.get("locale")
    project_slug = request.GET.get("project")
    search_identifiers = parse_bool(request.GET.get("search_identifiers"))
    search_match_case = parse_bool(request.GET.get("search_match_case"))
    search_match_whole_word = parse_bool(request.GET.get("search_match_whole_word"))

    if (
        not locale_code
        or not Locale.objects.visible().filter(code=locale_code).exists()
    ):
        locale_code = (
            get_project_locale_from_request(request, Locale.objects.visible())
            or "en-GB"
        )

    if page:
        try:
            page = int(page)
        except ValueError:
            page = 1
        # Single page fetch
        api_url = create_api_url(
            search,
            project_slug,
            locale_code,
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

        data = response.json()
        entities = data["results"]
        has_more = data["next"] is not None
    else:
        # Multi-page fetch
        entities = []
        has_more = True
        for p in range(1, pages + 1):
            if not has_more:
                break

            api_url = create_api_url(
                search,
                project_slug,
                locale_code,
                search_identifiers,
                search_match_case,
                search_match_whole_word,
                page=p,
            )

            try:
                response = requests.get(api_url)
                response.raise_for_status()
            except RequestException:
                raise Http404

            data = response.json()
            entities.extend(data["results"])
            has_more = data["next"] is not None

    html = render_to_string(
        "search/widgets/search_results.html",
        {
            "entities": entities,
            "locale": Locale.objects.get(code=locale_code),
            "search": search,
            "search_identifiers_enabled": search_identifiers,
            "match_case_enabled": search_match_case,
            "match_whole_word_enabled": search_match_whole_word,
        },
    )

    return JsonResponse(
        {"html": html, "has_more": has_more},
    )


def entity(request, pk):
    """Get corresponding entity given entity id."""
    api_url = f"{SITE_URL}/api/v2/entities/{pk}/?include_translations=True"
    try:
        response = requests.get(api_url)
        response.raise_for_status()
        data = response.json()
    except (RequestException, ValueError):
        raise Http404

    return render(request, "search/entity.html", {"entity": data})


def entity_alternate(request, project, resource, entity):
    """Get corresponding entity given entity."""

    entity = get_object_or_404(
        Entity,
        resource__project__slug=project,
        resource__path=resource,
        key__overlap=[entity],
    )

    return redirect(reverse("pontoon.entity", kwargs={"pk": entity.pk}))
