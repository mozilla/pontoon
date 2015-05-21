from django.contrib.auth.decorators import user_passes_test
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from pontoon.base.models import Entity, Project


@user_passes_test(lambda u: u.is_superuser)
def index(request, project_slug, locale):
    """Main translation interface."""
    project = get_object_or_404(Project.objects.available(), slug=project_slug)
    locale = get_object_or_404(project.locales, code__iexact=locale)

    return render(request, 'translate/index.html', {
        'project': project,
        'locale': locale,
    })


@user_passes_test(lambda u: u.is_superuser)
def entities(request, project_slug, locale):
    """Return all entities for the given project and locale in JSON."""
    project = get_object_or_404(Project.objects.available(), slug=project_slug)
    locale = get_object_or_404(project.locales, code__iexact=locale)

    entities = Entity.objects.filter(resource__project=project)
    data = [{
        'pk': entity.pk,
        'string': entity.string,
        'marked': entity.marked,
        'key': entity.key,
        'path': entity.resource.path,
        'comment': entity.comment,
        'translations': [translation.serialize() for translation in
                         entity.translation_set.filter(locale=locale)],
    } for entity in entities]

    return JsonResponse(data, safe=False)


@user_passes_test(lambda u: u.is_superuser)
def translations(request, entity_pk, locale_code):
    """Fetch or update translations for the given entity."""
    entity = get_object_or_404(Entity, pk=entity_pk)
    locale = get_object_or_404(entity.resource.project.locales, code__iexact=locale_code)

    if request.method == 'POST':
        string = request.POST.get('string', None)
        if not string:
            return JsonResponse({'reason': 'Missing string parameter.'}, status=400)

        entity.add_translation(string, locale, request.user)
    elif request.method != 'GET':
        return JsonResponse({'reason': 'Method not allowed.'}, status=405)

    translations = entity.translation_set.filter(locale=locale)
    return JsonResponse([t.serialize() for t in translations], safe=False)


@user_passes_test(lambda u: u.is_superuser)
def projects(request):
    """Fetch all available projects."""
    projects = [project.serialize() for project in Project.objects.available()]
    return JsonResponse(projects, safe=False)
