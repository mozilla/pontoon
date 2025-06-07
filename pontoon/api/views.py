from datetime import datetime, timedelta

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.timezone import make_aware
from django.views.decorators.http import require_GET

from pontoon.actionlog.models import ActionLog
from pontoon.api.filters import TermFilter, TranslationMemoryFilter

from pontoon.base.models import (
    Locale as LocaleModel,
    Project as ProjectModel,
    ProjectLocale as ProjectLocaleModel,
    TranslationMemoryEntry as TranslationMemoryEntryModel,
)
from pontoon.tags.models import Tag as TagModel
from pontoon.terminology.models import (
    Term as TermModel,
    TermTranslation as TermTranslationModel,
)

from .serializers import LocaleSerializer, ProjectSerializer, TermSerializer, TranslationMemorySerializer


@require_GET
@login_required(redirect_field_name="", login_url="/403")
def get_user_actions(request, date, slug):
    try:
        start_date = make_aware(datetime.strptime(date, "%Y-%m-%d"))
    except ValueError:
        return JsonResponse(
            {
                "error": "Invalid date format. Please use YYYY-MM-DD.",
            },
            status=400,
        )

    end_date = start_date + timedelta(days=1)

    try:
        project = ProjectModel.objects.get(slug=slug)
    except ProjectModel.DoesNotExist:
        return JsonResponse(
            {
                "error": "Project not found. Please use a valid project slug.",
            },
            status=404,
        )

    actions = ActionLog.objects.filter(
        action_type__startswith="translation:",
        created_at__gte=start_date,
        created_at__lt=end_date,
        translation__entity__resource__project=project,
    )

    actions = actions.prefetch_related(
        "performed_by__profile",
        "translation__entity__resource",
        "translation__errors",
        "translation__warnings",
        "translation__locale",
        "entity__resource",
        "locale",
    )

    output = []

    for action in actions:
        user = action.performed_by
        locale = action.locale or action.translation.locale
        entity = action.entity or action.translation.entity
        resource = entity.resource

        data = {
            "type": action.action_type,
            "date": action.created_at,
            "user": {
                "pk": user.pk,
                "name": user.display_name,
                "system_user": user.profile.system_user,
            },
            "locale": {
                "pk": locale.pk,
                "code": locale.code,
                "name": locale.name,
            },
            "entity": {
                "pk": entity.pk,
                "key": entity.key,
            },
            "resource": {
                "pk": resource.pk,
                "path": resource.path,
                "format": resource.format,
            },
        }

        if action.translation:
            data["translation"] = action.translation.serialize()

        output.append(data)

    return JsonResponse(
        {
            "actions": output,
            "project": {
                "pk": project.pk,
                "slug": project.slug,
                "name": project.name,
            },
        }
    )


class LocaleListView(generics.ListAPIView):
    queryset = LocaleModel.objects.all()
    serializer_class = LocaleSerializer


class LocaleIndividualView(generics.RetrieveAPIView):
    queryset = LocaleModel.objects.all()
    serializer_class = LocaleSerializer
    lookup_field = "code"


class ProjectListView(generics.ListAPIView):
    queryset = ProjectModel.objects.all()
    serializer_class = ProjectSerializer


class ProjectIndividualView(generics.RetrieveAPIView):
    queryset = ProjectModel.objects.all()
    serializer_class = ProjectSerializer
    lookup_field = "slug"


class TermSearchListView(generics.ListAPIView):
    queryset = TermModel.objects.all()
    serializer_class = TermSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = TermFilter

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset.distinct()

class TranslationMemorySearchListView(generics.ListAPIView):
    queryset = TranslationMemoryEntryModel.objects.all()
    serializer_class = TranslationMemorySerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = TranslationMemoryFilter

    def get_queryset(self):
        # Only return results if at least one filter param is set
        if not self.request.query_params:
            return TranslationMemoryEntryModel.objects.none()
        return TranslationMemoryEntryModel.objects.all()

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset
