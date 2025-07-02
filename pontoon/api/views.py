from datetime import datetime, timedelta

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.exceptions import ValidationError

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import JsonResponse
from django.utils.timezone import make_aware
from django.views.decorators.http import require_GET

from pontoon.actionlog.models import ActionLog
from pontoon.api.filters import TermFilter, TranslationMemoryFilter
from pontoon.base.models import (
    Locale,
    Project,
    ProjectLocale,
    TranslationMemoryEntry,
)
from pontoon.terminology.models import (
    Term,
)

from .serializers import (
    NestedLocaleSerializer,
    NestedProjectLocaleSerializer,
    NestedProjectSerializer,
    TermSerializer,
    TranslationMemorySerializer,
)


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
        project = Project.objects.get(slug=slug)
    except Project.DoesNotExist:
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
    serializer_class = NestedLocaleSerializer

    def get_queryset(self):
        locales = Locale.objects.prefetch_related("project_locale__project")
        return locales.stats_data()


class LocaleIndividualView(generics.RetrieveAPIView):
    serializer_class = NestedLocaleSerializer
    lookup_field = "code"

    def get_queryset(self):
        locales = Locale.objects.prefetch_related("project_locale__project")
        return locales.stats_data()


class ProjectListView(generics.ListAPIView):
    serializer_class = NestedProjectSerializer

    def get_queryset(self):
        query_params = self.request.query_params
        include_disabled = query_params.get("include_disabled")
        include_system = query_params.get("include_system")

        base_queryset = (
            Project.objects.visible()
            .visible_for(self.request.user)
            .prefetch_related("project_locale__locale", "contact", "tags")
            .stats_data()
        )
        filters = Q()
        if include_disabled is not None:
            filters |= Q(disabled=True)
        if include_system is not None:
            filters |= Q(system_project=True)

        if filters:
            return base_queryset.union(Project.objects.stats_data().filter(filters))

        return base_queryset


class ProjectIndividualView(generics.RetrieveAPIView):
    serializer_class = NestedProjectSerializer
    lookup_field = "slug"

    def get_queryset(self):
        queryset = (
            Project.objects.all()
            .prefetch_related("project_locale__locale", "contact", "tags")
            .stats_data()
        )

        return queryset


class ProjectLocaleIndividualView(generics.RetrieveAPIView):
    queryset = ProjectLocale.objects.all().prefetch_related("project", "locale")
    serializer_class = NestedProjectLocaleSerializer

    def get_object(self):
        slug = self.kwargs["slug"]
        code = self.kwargs["code"]
        return generics.get_object_or_404(
            ProjectLocale, project__slug=slug, locale__code=code
        )


class TermSearchListView(generics.ListAPIView):
    serializer_class = TermSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = TermFilter

    def get_queryset(self):
        query_params = self.request.query_params
        text = query_params.get("text")
        locale = query_params.get("locale")

        # Enforce required query parameters
        if not text or not locale:
            raise ValidationError(
                {"detail": "Both 'text' and 'locale' query parameters are required."}
            )

        return Term.objects.all()

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset.prefetch_related("translations__locale")


class TranslationMemorySearchListView(generics.ListAPIView):
    serializer_class = TranslationMemorySerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = TranslationMemoryFilter

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return TranslationMemoryEntry.objects.none()

        query_params = self.request.query_params
        text = query_params.get("text")
        locale = query_params.get("locale")

        # Enforce required query parameters
        if not text or not locale:
            raise ValidationError(
                {"detail": "Both 'text' and 'locale' query parameters are required."}
            )

        return TranslationMemoryEntry.objects.all()

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset.prefetch_related("project", "locale")
