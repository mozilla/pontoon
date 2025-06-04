import django_filters


class TermFilter(django_filters.FilterSet):
    pass

    # def resolve_term_search(self, info, search, locale):
    #     term_query = Q(text__icontains=search)

    #     translation_query = Q(translations__text__icontains=search) & Q(
    #         translations__locale__code=locale
    #     )

    #     # Prefetch translations for the specified locale
    #     prefetch_translations = Prefetch(
    #         "translations",
    #         queryset=TermTranslationModel.objects.filter(locale__code=locale),
    #         to_attr="locale_translations",
    #     )

    #     # Perform the query on the Term model and prefetch translations
    #     return (
    #         TermModel.objects.filter(term_query | translation_query)
    #         .prefetch_related(prefetch_translations)
    #         .distinct()
    #     )
