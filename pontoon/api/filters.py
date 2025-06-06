from django_filters import FilterSet, CharFilter
from django.db.models import Q

from pontoon.base.models import (
    TranslationMemoryEntry as TranslationMemoryEntryModel,
)

from pontoon.terminology.models import (
    Term as TermModel,
)

class TermFilter(FilterSet):
    search = CharFilter(method='filter_search')
    locale = CharFilter(method='filter_locale')

    class Meta:
        model = TermModel
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(text__icontains=value)

    def filter_locale(self, queryset, name, value):
        return queryset.filter(translations__locale__code=value)

class TranslationMemoryFilter(FilterSet):
    search = CharFilter(method='filter_search')
    locale = CharFilter(method='filter_locale')

    class Meta:
        model = TranslationMemoryEntryModel
        fields = []

    def filter_search(self, queryset, name, value):
        return queryset.filter(Q(Q(source__icontains=value) | Q(target__icontains=value)))

    def filter_locale(self, queryset, name, value):
        return queryset.filter(locale__code=value)