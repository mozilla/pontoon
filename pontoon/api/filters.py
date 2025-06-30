from django_filters import CharFilter, FilterSet

from django.db.models import Q

from pontoon.base.models import (
    TranslationMemoryEntry,
)
from pontoon.terminology.models import (
    Term,
)


class TermFilter(FilterSet):
    text = CharFilter(method="filter_text")
    locale = CharFilter(method="filter_locale")

    class Meta:
        model = Term
        fields = []

    def filter_text(self, queryset, name, value):
        return queryset.filter(text__icontains=value)

    def filter_locale(self, queryset, name, value):
        return queryset.filter(translations__locale__code=value)


class TranslationMemoryFilter(FilterSet):
    text = CharFilter(method="filter_text")
    locale = CharFilter(method="filter_locale")

    class Meta:
        model = TranslationMemoryEntry
        fields = []

    def filter_text(self, queryset, name, value):
        return queryset.filter(
            Q(Q(source__icontains=value) | Q(target__icontains=value))
        )

    def filter_locale(self, queryset, name, value):
        return queryset.filter(locale__code=value)
