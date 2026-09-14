from moz.l10n.resource import serialize_resource

from django.db.models import Q

from pontoon.base.models import (
    Locale,
    Resource as DbResource,
    Translation,
)
from pontoon.sync.core.translations_to_repo import (
    build_moz_l10n_resource,
    build_translated_resource,
)


def serialize_translated_resource(db_res: DbResource, locale: Locale) -> str:
    res = build_moz_l10n_resource(db_res)
    translations = {
        tuple(tx.entity.key): tx
        for tx in Translation.objects.filter(
            entity__obsolete=False,
            entity__resource=db_res,
            locale=locale,
            active=True,
        )
        .filter(
            Q(approved=True)
            | Q(pretranslated=True, warnings__isnull=True)
            | Q(fuzzy=True)
        )
        .select_related("entity")
        .iterator()
    }
    tr_res = build_translated_resource(locale, translations, res)

    lc_plurals = locale.cldr_plurals_list()
    return "".join(serialize_resource(tr_res, gettext_plurals=lc_plurals))
