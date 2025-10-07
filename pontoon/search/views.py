import requests

from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse

from pontoon.base.models.entity import Entity


BASE_URL = "http://localhost:8000/api/v2"


def entity(request, pk):
    """Get corresponding entity given entity."""
    api_url = f"{BASE_URL}/entities/{pk}/?include_translations"
    res = requests.get(api_url)

    if res.status_code == 200:
        entity = res.json()
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
