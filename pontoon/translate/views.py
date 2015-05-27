from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from pontoon.base.models import Entity, Project


def index(request, project_slug, locale):
    project = get_object_or_404(Project.objects.available(), slug=project_slug)
    locale = get_object_or_404(project.locales, code__iexact=locale)

    return render(request, 'translate/index.html', {
        'project': project,
        'locale': locale,
    })


def entities(request, project_slug, locale):
    project = get_object_or_404(Project.objects.available(), slug=project_slug)
    locale = get_object_or_404(project.locales, code__iexact=locale)

    entities = Entity.objects.filter(resource__project=project)
    data = []
    for entity in entities:
        approved = entity.approved_translation(locale=locale)
        data.append({
            'pk': entity.pk,
            'marked': entity.marked,
            'approved_translation': approved.serialize() if approved else None,
            'translations': [translation.serialize() for translation in
                             entity.translation_set.filter(locale=locale)],
        })

    return JsonResponse(data, safe=False)
