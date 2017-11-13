from factory import (
    Sequence,
    SubFactory
)
from factory.django import DjangoModelFactory

from pontoon.base.tests import LocaleFactory
from pontoon.terminology.models import (
    Term,
    TermTranslation
)


class TermFactory(DjangoModelFactory):
    term_id = Sequence(lambda n: 'term_{}'.format(n))
    source_term = Sequence(lambda n: 'source terms: {}'.format(n))
    source_term_singulars = Sequence(lambda n: 'source term {}'.format(n))

    class Meta:
        model = Term


class TermTranslation(DjangoModelFactory):
    locale = SubFactory(LocaleFactory)
    term = SubFactory(TermFactory)
    text = Sequence(lambda n: 'term translation {}'.format(n))

    class Meta:
        model = TermTranslation
