from datetime import datetime, timedelta
from types import SimpleNamespace

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.contrib.auth.decorators import login_required
from django.db.models import Prefetch, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.timezone import make_aware
from django.views.decorators.http import require_GET

from pontoon.actionlog.models import ActionLog

# from pontoon.api.authentication import PersonalAccessTokenAuthentication
from pontoon.api.filters import TermFilter, TranslationMemoryFilter
from pontoon.base import forms
from pontoon.base.models import (
    Locale,
    Project,
    ProjectLocale,
    Resource,
    TranslationMemoryEntry,
)
from pontoon.base.models.entity import Entity
from pontoon.base.models.translation import Translation
from pontoon.pretranslation.pretranslate import get_pretranslation
from pontoon.terminology.models import (
    Term,
)

from .serializers import (
    TRANSLATION_STATS_FIELDS,
    EntitySearchSerializer,
    EntitySerializer,
    NestedEntitySerializer,
    NestedIndividualLocaleSerializer,
    NestedIndividualProjectSerializer,
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
                "username": user.username,
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


class UserActionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, date, slug):
        try:
            start_date = make_aware(datetime.strptime(date, "%Y-%m-%d"))
        except ValueError:
            raise ValidationError("Bad Request in kwarg: 'date'.")

        end_date = start_date + timedelta(days=1)

        project = generics.get_object_or_404(Project, slug=slug)

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

        return Response(
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
        qs = Locale.objects.available()

        fields_param = self.request.query_params.get("fields", "")
        requested = set(f.strip() for f in fields_param.split(",") if f.strip())

        # Only prefetch project data when requested
        needs_projects = not requested or requested & {"projects"}
        if needs_projects:
            qs = qs.prefetch_related(
                Prefetch(
                    "project_locale",
                    queryset=ProjectLocale.objects.visible().select_related("project"),
                    to_attr="fetched_project_locales",
                )
            )

        # Only gather stats when requested
        needs_stats = not requested or requested & set(TRANSLATION_STATS_FIELDS)
        if needs_stats:
            qs = qs.stats_data()

        return qs.distinct().order_by("code")


class LocaleIndividualView(generics.RetrieveAPIView):
    serializer_class = NestedIndividualLocaleSerializer
    lookup_field = "code"

    def get_queryset(self):
        queryset = Locale.objects.prefetch_related(
            Prefetch(
                "project_locale",
                queryset=ProjectLocale.objects.visible().select_related("project"),
                to_attr="fetched_project_locales",
            )
        ).distinct()
        return queryset.stats_data()


class ProjectListView(generics.ListAPIView):
    serializer_class = NestedProjectSerializer

    def get_queryset(self):
        query_params = self.request.query_params
        include_disabled = query_params.get("include_disabled")
        include_system = query_params.get("include_system")

        queryset = (
            Project.objects.visible()
            .visible_for(self.request.user)
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

        filters = Q()
        if include_disabled is not None:
            filters |= Q(disabled=True)
        if include_system is not None:
            filters |= Q(system_project=True)
        if filters:
            queryset = queryset | Project.objects.filter(filters).distinct()
        return queryset.stats_data().order_by("slug")


class ProjectIndividualView(generics.RetrieveAPIView):
    serializer_class = NestedIndividualProjectSerializer
    lookup_field = "slug"

    def get_queryset(self):
        queryset = (
            Project.objects.available()
            .visible_for(self.request.user)
            .prefetch_related(
                Prefetch(
                    "project_locale",
                    queryset=ProjectLocale.objects.visible().select_related("locale"),
                    to_attr="fetched_project_locales",
                ),
                "contact",
                "tags",
            )
        ).distinct()

        return queryset.stats_data()


class EntityListView(generics.ListAPIView):
    serializer_class = EntitySerializer

    def get_queryset(self):
        return (
            Entity.objects.filter(resource__project__disabled=False)
            .prefetch_related(
                "resource",
                "resource__project",
            )
            .order_by("id")
        )


class EntityIndividualView(generics.RetrieveAPIView):
    serializer_class = NestedEntitySerializer

    def get_queryset(self):
        return Entity.objects.filter(
            resource__project__disabled=False
        ).prefetch_related(
            Prefetch(
                "translation_set",
                queryset=Translation.objects.filter(approved=True).select_related(
                    "locale"
                ),
                to_attr="filtered_translations",
            ),
        )

    def get_object(self):
        queryset = self.get_queryset()
        if "pk" in self.kwargs:
            return get_object_or_404(queryset, pk=self.kwargs["pk"])

        return get_object_or_404(
            queryset,
            resource__project__slug=self.kwargs["project"],
            resource__path=self.kwargs["resource"],
            key__overlap=[self.kwargs["entity"]],
        )


class ProjectLocaleIndividualView(generics.RetrieveAPIView):
    serializer_class = NestedProjectLocaleSerializer

    def get_object(self):
        slug = self.kwargs["slug"]
        code = self.kwargs["code"]

        project = get_object_or_404(
            Project,
            slug=slug,
        )

        queryset = (
            ProjectLocale.objects.all()
            .filter(project__slug=slug, locale__code=code)
            .prefetch_related("project", "locale")
            .stats_data(project)
        )

        obj = get_object_or_404(queryset, project__slug=slug, locale__code=code)

        return obj


class TermSearchListView(generics.ListAPIView):
    serializer_class = TermSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TermFilter
    queryset = Term.objects.prefetch_related("translations__locale")


class TranslationMemorySearchListView(generics.ListAPIView):
    serializer_class = TranslationMemorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TranslationMemoryFilter
    queryset = TranslationMemoryEntry.objects.select_related("project", "locale")


class TranslationSearchListView(generics.ListAPIView):
    serializer_class = EntitySearchSerializer

    def get_queryset(self):
        query_params = self.request.query_params.copy()
        text = query_params.get("text")
        locale = query_params.get("locale")

        errors = {}
        if not text:
            errors["text"] = ["This field is required."]
        if not locale:
            errors["locale"] = ["This field is required."]
        if errors:
            raise ValidationError(errors)

        query_params["search"] = query_params.pop("text")[0]
        query_params["project"] = query_params.get("project", "all-projects")

        form = forms.GetEntitiesForm(query_params)

        if not form.is_valid():
            raise ValidationError(form.errors)

        locale_code = form.cleaned_data["locale"]
        locale = get_object_or_404(Locale, code=locale_code)

        project_slug = form.cleaned_data["project"]

        if project_slug == "all-projects":
            project = Project(slug="all-projects")
        else:
            project = get_object_or_404(Project, slug=project_slug)

        restrict_to_keys = (
            "search",
            "search_identifiers",
            "search_match_case",
            "search_match_whole_word",
        )
        form_data = {
            k: form.cleaned_data[k] for k in restrict_to_keys if k in form.cleaned_data
        }

        try:
            entities = (
                Entity.for_project_locale(
                    self.request.user, project, locale, status="translated", **form_data
                )
                .prefetch_related(
                    (
                        Prefetch(
                            "translation_set",
                            queryset=Translation.objects.filter(
                                locale__code=locale_code, approved=True
                            ).select_related("locale"),
                            to_attr="filtered_translations",
                        )
                    ),
                )
                .select_related("resource__project")
            )
        except ValueError as error:
            raise ValueError(error)

        return entities


MAX_TEXT_CHARS = 2048
MAX_TEXT_BYTES = MAX_TEXT_CHARS * 4


class PretranslationView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [PersonalAccessTokenAuthentication]

    def post(self, request):
        string_format = request.query_params.get("string_format")
        locale = request.query_params.get("locale")

        if not request.body:
            raise ValidationError({"text": ["This field is required."]})

        if len(request.body) > MAX_TEXT_BYTES:
            raise ValidationError({"text": ["Payload too large."]})

        try:
            text = request.body.decode("utf-8", errors="replace")
        except Exception:
            raise ValidationError({"text": ["Unable to decode request body as UTF-8."]})

        errors = {}
        if not text.strip():
            errors["text"] = ["This field is required."]
        elif len(text) > MAX_TEXT_CHARS:
            errors["text"] = ["Text exceeds maximum length of 2048 characters."]
        if not locale:
            errors["locale"] = ["This field is required."]
        if string_format and string_format not in {
            Resource.Format.ANDROID,
            Resource.Format.DTD,
            Resource.Format.FLUENT,
            Resource.Format.GETTEXT,
            Resource.Format.INI,
            Resource.Format.PLAIN_JSON,
            Resource.Format.PROPERTIES,
            Resource.Format.WEBEXT,
            Resource.Format.XCODE,
            Resource.Format.XLIFF,
        }:
            errors["format"] = ["Choose a correct format."]
        if errors:
            raise ValidationError(errors)

        locale = generics.get_object_or_404(Locale, code=locale)

        project = SimpleNamespace(slug="temp-project")
        resource = SimpleNamespace(project=project, format=string_format or "no-format")
        entity = SimpleNamespace(resource=resource, string=text)

        try:
            pretranslation = get_pretranslation(entity=entity, locale=locale)
        except Exception as e:
            return Response(
                {"error": str(e)},
                status=400,
            )

        return Response({"text": pretranslation[0], "author": pretranslation[1]})
