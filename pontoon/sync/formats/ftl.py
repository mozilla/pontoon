from __future__ import annotations

from fluent.syntax import FluentParser, FluentSerializer
from moz.l10n.formats.fluent import fluent_astify_entry
from moz.l10n.model import Entry, Message, Resource

from .common import VCSTranslation


parser = FluentParser()
serializer = FluentSerializer()


def parse(res: Resource[Message]):
    translations: list[VCSTranslation] = []
    order = 0
    for section in res.sections:
        for entry in section.entries:
            if isinstance(entry, Entry):
                assert len(entry.id) == 1
                key = entry.id[0]

                # Do not store comments in the string column
                comment = entry.comment
                entry.comment = ""
                entry.meta = []
                translation = serializer.serialize_entry(fluent_astify_entry(entry))

                translations.append(
                    VCSTranslation(
                        key=key,
                        context=key,
                        order=order,
                        string=translation,
                        source_string=translation,
                        comments=[comment] if comment else None,
                        group_comment=section.comment,
                        resource_comment=res.comment,
                    )
                )
                order += 1

    return translations
