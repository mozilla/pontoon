"""
During some database intensive operatations like e.g. import of large terminology files
it's better to load all terms to the memory to make access faster.
However, that approach isn't possible to maintain in the normally working webapp.

That's why this module provide classes that are able to control how to access.
"""
from collections import defaultdict
import operator


class CachedDBTermIndex(object):
    @classmethod
    def get_terms_candidates(cls, phrase):
        """
        Keeps a memory index of terms for faster lookups. The first call will always take some time.
        Index is built from words extracted from terms. Entries can look like e.g.
        Term: Pontoon App, id = 1
        Term: Pontoon Author, id = 2
        {
           "Pontoon': [1,2],
           "App": [1],
           "Author": [2]
        }
        """

        from pontoon.terminology.models import Term

        if not hasattr(cls, '_term_index'):
            index = defaultdict(lambda: defaultdict(list))
            term_pk_singulars = (
                Term.objects
                    .order_by('-source_term')
                    .values_list('pk', 'source_term_singulars')
            )

            for term_pk, term_singulars in term_pk_singulars:
                for word in term_singulars.split():
                    index[word][term_singulars].append(term_pk)
            cls._term_index = index

        candidates = defaultdict(set)
        for word in phrase.split():
            for term_singulars, terms_pks in cls._term_index[word].items():
                candidates[term_singulars].update(terms_pks)
        return candidates

    @classmethod
    def reset(cls):
        """
        Remove all items from the memory.
        :return:
        """
        del cls._term_index


class DBTermIndex(object):
    @classmethod
    def get_terms_candidates(self, phrase):
        """
        Queries existing database and doesn't cache results.
        """
        from django.contrib.postgres.search import SearchQuery, SearchVector
        from pontoon.terminology.models import Term

        candidate_terms = defaultdict(set)

        # maps all words from a phrase into a union of SearchQuery objects
        # This
        search_words = reduce(
            operator.or_,
            [SearchQuery(w.lower(), config='simple') for w in phrase.split()]
        )
        terms = (
            Term.objects
            .annotate(search_field=SearchVector('source_term_singulars', config='simple'))
            .filter(search_field=search_words)
            .values_list('pk', 'source_term_singulars')
        )

        for term_pk, term_singulars in terms:
            candidate_terms[term_singulars].add(term_pk)

        return candidate_terms

    @classmethod
    def reset(self):
        pass
