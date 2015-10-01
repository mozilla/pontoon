import factory

from pontoon.sync.vcs_models import VCSEntity, VCSTranslation


class VCSEntityFactory(factory.Factory):
    resource = None
    key = 'key'
    string = 'string'
    string_plural = ''
    comments = factory.List([])
    source = factory.List([])
    order = factory.Sequence(lambda n: n)

    class Meta:
        model = VCSEntity


class VCSTranslationFactory(factory.Factory):
    key = factory.Sequence(lambda n: 'key-{0}'.format(n))
    strings = factory.Dict({})
    comments = factory.List([])
    fuzzy = False

    class Meta:
        model = VCSTranslation
