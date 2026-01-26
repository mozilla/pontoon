from datetime import datetime, timedelta
from types import SimpleNamespace

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.exceptions import PermissionDenied, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django.db.models import Prefetch, Q
from django.shortcuts import get_object_or_404
from django.utils.timezone import make_aware

from pontoon.actionlog.models import ActionLog
from pontoon.api.authentication import (
    IsPretranslator,
    PersonalAccessTokenAuthentication,
)
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
from pontoon.settings.base import PRETRANSLATION_API_MAX_CHARS
from pontoon.terminology.models import (
    Term,
    TermTranslation,
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


class RequestFieldsMixin:
    """Mixin to parse the 'fields' query parameter into a set of requested field names."""

    def request_fields(self):
        fields_param = self.request.query_params.get("fields", "")
        return set(fs for f in fields_param.split(",") if (fs := f.strip()))


class UserActionsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, date, slug):
        try:
            start_date = make_aware(datetime.strptime(date, "%Y-%m-%d"))
        except ValueError:
            raise ValidationError("Bad Request in kwarg: 'date'.")

        end_date = start_date + timedelta(days=1)

        project = generics.get_object_or_404(Project, slug=slug)
        if not Project.objects.filter(pk=project.pk).visible_for(request.user).exists():
            raise PermissionDenied(
                "You do not have permission to access data for this project."
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


class LocaleListView(RequestFieldsMixin, generics.ListAPIView):
    serializer_class = NestedLocaleSerializer

    def get_queryset(self):
        qs = Locale.objects.visible()

        requested = self.request_fields()

        # Only prefetch project data when requested
        if not requested or "projects" in requested:
            qs = qs.prefetch_related(
                Prefetch(
                    "project_locale",
                    queryset=ProjectLocale.objects.visible().select_related("project"),
                    to_attr="fetched_project_locales",
                )
            )

        # Only gather stats when requested
        if not requested or requested & set(TRANSLATION_STATS_FIELDS):
            qs = qs.stats_data()

        return qs.distinct().order_by("code")


class LocaleIndividualView(RequestFieldsMixin, generics.RetrieveAPIView):
    serializer_class = NestedIndividualLocaleSerializer
    lookup_field = "code"

    def get_queryset(self):
        qs = Locale.objects.visible()

        requested = self.request_fields()

        # Only prefetch project data when requested
        if not requested or "projects" in requested:
            qs = qs.prefetch_related(
                Prefetch(
                    "project_locale",
                    queryset=ProjectLocale.objects.visible().select_related("project"),
                    to_attr="fetched_project_locales",
                )
            )

        # Only gather stats when requested
        if not requested or requested & set(TRANSLATION_STATS_FIELDS):
            qs = qs.stats_data()

        return qs


class ProjectListView(RequestFieldsMixin, generics.ListAPIView):
    serializer_class = NestedProjectSerializer

    def get_queryset(self):
        query_params = self.request.query_params
        include_disabled = query_params.get("include_disabled", "").lower()
        include_system = query_params.get("include_system", "").lower()

        qs = Project.objects.visible().visible_for(self.request.user)

        requested = self.request_fields()

        # Only prefetch locale data when requested
        if not requested or "locales" in requested:
            qs = qs.prefetch_related(
                Prefetch(
                    "project_locale",
                    queryset=ProjectLocale.objects.visible().select_related("locale"),
                    to_attr="fetched_project_locales",
                )
            )

        # Only prefetch contact when requested
        if not requested or "contact" in requested:
            qs = qs.prefetch_related("contact")

        # Only prefetch tags when requested
        if not requested or "tags" in requested:
            qs = qs.prefetch_related("tags")

        filters = Q()
        if include_disabled == "true":
            filters |= Q(disabled=True)
        if include_system == "true":
            filters |= Q(system_project=True)
        if filters:
            qs = qs | Project.objects.filter(filters).distinct()

        # Only gather stats when requested
        if not requested or requested & set(TRANSLATION_STATS_FIELDS):
            qs = qs.stats_data()

        return qs.order_by("slug")


class ProjectIndividualView(RequestFieldsMixin, generics.RetrieveAPIView):
    serializer_class = NestedIndividualProjectSerializer
    lookup_field = "slug"

    def get_queryset(self):
        qs = Project.objects.available().visible_for(self.request.user)

        requested = self.request_fields()

        # Only prefetch locale data when requested
        if not requested or "locales" in requested:
            qs = qs.prefetch_related(
                Prefetch(
                    "project_locale",
                    queryset=ProjectLocale.objects.visible().select_related("locale"),
                    to_attr="fetched_project_locales",
                )
            )

        # Only prefetch contact when requested
        if not requested or "contact" in requested:
            qs = qs.prefetch_related("contact")

        # Only prefetch tags when requested
        if not requested or "tags" in requested:
            qs = qs.prefetch_related("tags")

        # Only gather stats when requested
        if not requested or requested & set(TRANSLATION_STATS_FIELDS):
            qs = qs.stats_data()

        return qs.distinct()


class EntityListView(RequestFieldsMixin, generics.ListAPIView):
    serializer_class = EntitySerializer

    def get_queryset(self):
        visible_projects = Project.objects.visible().visible_for(self.request.user)
        qs = Entity.objects.filter(
            resource__project__in=visible_projects, resource__project__disabled=False
        ).prefetch_related("resource")

        requested = self.request_fields()

        if not requested or "project" in requested:
            qs = qs.prefetch_related("resource__project")

        return qs.order_by("id")


class EntityIndividualView(RequestFieldsMixin, generics.RetrieveAPIView):
    serializer_class = NestedEntitySerializer

    def get_queryset(self):
        visible_projects = Project.objects.visible().visible_for(self.request.user)
        qs = Entity.objects.filter(
            resource__project__in=visible_projects, resource__project__disabled=False
        )

        requested = self.request_fields()

        if not requested or "translations" in requested:
            qs = qs.prefetch_related(
                Prefetch(
                    "translation_set",
                    queryset=Translation.objects.filter(approved=True).select_related(
                        "locale"
                    ),
                    to_attr="filtered_translations",
                )
            )
        return qs

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


class ProjectLocaleIndividualView(RequestFieldsMixin, generics.RetrieveAPIView):
    serializer_class = NestedProjectLocaleSerializer

    def get_queryset(self):
        slug = self.kwargs["slug"]
        code = self.kwargs["code"]

        qs = ProjectLocale.objects.all().filter(project__slug=slug, locale__code=code)

        requested = self.request_fields()

        # Only prefetch locale when requested
        if not requested or "locale" in requested:
            qs = qs.prefetch_related("locale")

        # Only prefetch project when requested
        if not requested or "project" in requested:
            qs = qs.prefetch_related("project")

        # Only gather stats when requested
        if not requested or requested & set(TRANSLATION_STATS_FIELDS):
            project = get_object_or_404(
                Project,
                slug=slug,
            )
            qs = qs.stats_data(project)

        return qs

    def get_object(self):
        queryset = self.get_queryset()
        slug = self.kwargs["slug"]
        code = self.kwargs["code"]

        obj = get_object_or_404(queryset, project__slug=slug, locale__code=code)

        return obj


class TermSearchListView(RequestFieldsMixin, generics.ListAPIView):
    serializer_class = TermSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TermFilter

    def get_queryset(self):
        locale = self.request.query_params.get("locale")

        qs = Term.objects.all()

        requested = self.request_fields()

        # Only prefetch translation_text when requested
        if not requested or "translation_text" in requested:
            qs = qs.prefetch_related(
                (
                    Prefetch(
                        "translations",
                        queryset=TermTranslation.objects.filter(
                            locale__code=locale
                        ).select_related("locale"),
                        to_attr="filtered_translations",
                    )
                ),
            ).select_related("entity")

        return qs


class TranslationMemorySearchListView(generics.ListAPIView):
    serializer_class = TranslationMemorySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_class = TranslationMemoryFilter
    queryset = TranslationMemoryEntry.objects.select_related("project", "locale")


class TranslationSearchListView(RequestFieldsMixin, generics.ListAPIView):
    serializer_class = EntitySearchSerializer

    def get_queryset(self):
        query_params = self.request.query_params.copy()
        text = query_params.get("text")
        locale = query_params.get("locale")

        if query_params.get("search_identifiers", "").lower() != "true":
            query_params.pop("search_identifiers", None)
        if query_params.get("search_match_case", "").lower() != "true":
            query_params.pop("search_match_case", None)
        if query_params.get("search_match_whole_word", "").lower() != "true":
            query_params.pop("search_match_whole_word", None)

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
            qs = Entity.for_project_locale(
                self.request.user, project, locale, status="translated", **form_data
            ).select_related("resource__project")

            requested = self.request_fields()

            # Only prefetch translation_text when requested
            if not requested or "translation" in requested:
                qs = qs.prefetch_related(
                    (
                        Prefetch(
                            "translation_set",
                            queryset=(
                                Translation.objects.filter(locale=locale, approved=True)
                            ).select_related("locale"),
                            to_attr="active_translations",
                        )
                    ),
                )

        except ValueError as error:
            raise ValueError(error)

        return qs


class PretranslationView(APIView):
    permission_classes = [IsAuthenticated, IsPretranslator]
    authentication_classes = [PersonalAccessTokenAuthentication]

    def post(self, request):
        resource_format = request.query_params.get("resource_format")
        locale = request.query_params.get("locale")

        errors = {}
        try:
            text = request.body.decode("utf-8")
        except UnicodeDecodeError:
            errors["text"] = ["Unable to decode request body as UTF-8."]
            text = None

        if text is not None:
            if len(text) > PRETRANSLATION_API_MAX_CHARS:
                errors["text"] = [
                    f"Text exceeds maximum length of {PRETRANSLATION_API_MAX_CHARS} characters."
                ]
            elif not text.strip():
                errors["text"] = ["This field is required."]

        if not locale:
            errors["locale"] = ["This field is required."]
        if resource_format and resource_format not in set(Resource.Format):
            errors["resource_format"] = ["Choose a correct resource format."]
        if errors:
            raise ValidationError(errors)

        locale = generics.get_object_or_404(Locale, code=locale)

        project = SimpleNamespace(slug="temp-project")
        resource = SimpleNamespace(project=project, format=resource_format or None)
        entity = SimpleNamespace(resource=resource, string=text)

        try:
            pretranslation = get_pretranslation(entity=entity, locale=locale)
        except Exception as e:
            return Response(
                {
                    "error": f"An error occurred: {str(e)}. Please verify the resource format and syntax."
                },
                status=400,
            )

        return Response({"text": pretranslation[0], "author": pretranslation[1]})
