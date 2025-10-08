from rest_framework.request import Request

from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from pontoon.api.views import EntityIndividualView
from pontoon.base.models.entity import Entity


BASE_URL = "http://localhost:8000/api/v2"


def translation_search(request):
    """Get corresponding entity given entity."""
    expected_params = {
        "search": None,
        "p": None,
        "l": None,
        "identifiers": None,
        "match_case": None,
        "match_word": None,
    }

    # Extract query parameters dynamically
    query_params = {
        key: request.GET.get(key, default) for key, default in expected_params.items()
    }

    # Example: Use the extracted parameters
    if query_params["search"]:
        # Do something with query_params["search"]
        pass

    # Build the API URL or perform further logic
    return render(request, "search/results.html", {"query_params": query_params})


def entity(request, pk):
    """Get corresponding entity given entity."""

    # Modify the request object to include translations
    drf_request = Request(request)
    query_params = drf_request.query_params.copy()
    query_params["include_translations"] = ""
    drf_request._request.GET = query_params

    entity_view = EntityIndividualView.as_view()
    response = entity_view(request, pk=pk)

    if response.status_code == 200:
        entity_data = response.data
        return render(
            request,
            "search/entity.html",
            {
                "entity": entity_data.get("entity", []),
                "project": entity_data.get("project", []),
                "resource": entity_data.get("resource", []),
                "translations": entity_data.get("translations", []),
            },
        )
    else:
        raise Http404("Entity not found")


def entity_alternate(request, project, resource, entity):
    """Get corresponding entity given entity."""

    entity = get_object_or_404(
        Entity,
        resource__project__slug=project,
        resource__path=resource,
        key__overlap=[entity],
    )

    return redirect(reverse("pontoon.entity", kwargs={"pk": entity.pk}))
