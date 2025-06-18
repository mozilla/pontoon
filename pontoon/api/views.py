from datetime import datetime, timedelta

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.exceptions import ValidationError
from rest_framework import generics

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.timezone import make_aware
from django.views.decorators.http import require_GET

from pontoon.actionlog.models import ActionLog
from pontoon.api.filters import TermFilter, TranslationMemoryFilter
from pontoon.base.models import (
    Entity as EntityModel,
    Locale as LocaleModel,
    Project as ProjectModel,
    ProjectLocale as ProjectLocaleModel,
    Translation as TranslationModel,
    TranslationMemoryEntry as TranslationMemoryEntryModel,
)
from pontoon.terminology.models import (
    Term as TermModel,
)

from .serializers import (
    LocaleSerializer,
    NestedLocaleSerializer,
    NestedProjectLocaleSerializer,
    NestedProjectSerializer,
    TermSerializer,
    TranslationMemorySerializer,
    TranslationSerializer,
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


class MultipleFieldLookupMixin:
    """
    Apply this mixin to any view or viewset to get multiple field filtering
    based on a `lookup_fields` attribute, instead of the default single field filtering.
    """

    def get_object(self):
        queryset = self.get_queryset()  # Get the base queryset
        queryset = self.filter_queryset(queryset)  # Apply any filter backends
        filter = {}
        for field in self.lookup_fields:
            if self.kwargs.get(field):  # Ignore empty fields.
                filter[field] = self.kwargs[field]
        obj = generics.get_object_or_404(queryset, **filter)  # Lookup the object
        # self.check_object_permissions(self.request, obj)
        return obj


class LocaleListView(generics.ListAPIView):
    queryset = LocaleModel.objects.all()
    serializer_class = LocaleSerializer


class LocaleIndividualView(generics.RetrieveAPIView):
    queryset = LocaleModel.objects.all()
    serializer_class = NestedLocaleSerializer
    lookup_field = "code"


class ProjectListView(generics.ListAPIView):
    queryset = ProjectModel.objects.all()
    serializer_class = NestedProjectSerializer


class ProjectIndividualView(generics.RetrieveAPIView):
    queryset = ProjectModel.objects.all()
    serializer_class = NestedProjectSerializer
    lookup_field = "slug"


class ProjectLocaleIndividualView(generics.RetrieveAPIView):
    queryset = ProjectLocaleModel.objects.all()
    serializer_class = NestedProjectLocaleSerializer

    def get_object(self):
        slug = self.kwargs["slug"]
        code = self.kwargs["code"]
        return generics.get_object_or_404(
            ProjectLocaleModel, project__slug=slug, locale__code=code
        )


class TermSearchListView(generics.ListAPIView):
    serializer_class = TermSerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = TermFilter

    def get_queryset(self):
        query_params = self.request.query_params
        search = query_params.get("search")
        locale = query_params.get("locale")

        # Only return results if search param is set without locale param
        if search and not locale:
            raise ValidationError("Missing query parameters required with 'search': 'locale'.")

        return TermModel.objects.all()

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        return queryset


class TranslationMemorySearchListView(generics.ListAPIView):
    serializer_class = TranslationMemorySerializer

    filter_backends = [DjangoFilterBackend]
    filterset_class = TranslationMemoryFilter

    def get_queryset(self):
        query_params = self.request.query_params
        search = query_params.get("search")
        locale = query_params.get("locale")

        # Only return results if at least one filter param is set
        if not search and not locale:
            return TranslationMemoryEntryModel.objects.none()

        # Only return results if search param is not set by itself
        if search and not locale:
            raise ValidationError("Missing query parameters required with 'search': 'locale'.")

        return TranslationMemoryEntryModel.objects.all()

    def filter_queryset(self, queryset):
        queryset = super().filter_queryset(queryset)
        # return queryset
        return queryset


class EntityTranslationSearchListView(generics.ListAPIView):
    serializer_class = TranslationSerializer

    def get_queryset(self):
        query_params = self.request.query_params
        entity = query_params.get("entity")
        locale = query_params.get("locale")

        if not entity and not locale:
            raise ValidationError("Missing required query parameters: 'entity', 'locale'.")
        
        if not entity:
            raise ValidationError("Missing required query parameters: 'entity'.")
        
        if not locale:
            raise ValidationError("Missing required query parameters: 'locale'.")

        # Only return results if both params are set
        if entity and locale:
            entity = generics.get_object_or_404(EntityModel, pk=entity)
            locale = generics.get_object_or_404(LocaleModel, code=locale)
            plural_form = None if entity.string_plural == "" else 0

            queryset = (
                TranslationModel.objects.filter(
                    entity=entity,
                    plural_form=plural_form,
                    approved=True,
                )
                .exclude(locale=locale)
                .order_by('locale__code')
            )

            return queryset

        return TranslationModel.objects.none()

        # commented out for later inclusion
        # preferred_locales = []
        # if self.request.user.is_authenticated:
        #     preferred_locales = self.request.user.profile.preferred_locales.values_list(
        #         "code", flat=True
        #     )

        # payload = [
        #     _serialize_translation_values(translation, preferred_locales)
        #     for translation in translations
        # ]
