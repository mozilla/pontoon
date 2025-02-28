"""
Parser for the xliff translation format.
"""

from __future__ import annotations

from lxml import etree

from translate.storage import xliff

from .common import ParseError, VCSTranslation


class XLIFFResource:
    entities: dict[str, VCSTranslation]

    def __init__(self, path, source_resource: "XLIFFResource" | None = None):
        # Use entities from the source_resource if it's available.
        if source_resource:
            self.entities = source_resource.entities
            for entity in self.entities.values():
                entity.strings = {}
        else:
            self.entities = {}

        with open(path) as f:
            xml = f.read().encode("utf-8")

            try:
                xliff_file = xliff.xlifffile(xml)
            except etree.XMLSyntaxError as err:
                raise ParseError(f"Failed to parse {path}: {err}")

            for order, unit in enumerate(xliff_file.units):
                key = unit.getid()

                rich_target = unit.get_rich_target()
                target_string = str(rich_target[0]) if rich_target else None
                notes = unit.getnotes()

                self.entities[key] = VCSTranslation(
                    key=key,
                    context=unit.xmlelement.get("id"),
                    order=order,
                    strings={None: target_string} if target_string else {},
                    source_string=str(unit.rich_source[0]),
                    comments=notes.split("\n") if notes else None,
                )


def parse(path, source_path=None):
    source_resource = None if source_path is None else XLIFFResource(source_path)
    res = XLIFFResource(path, source_resource)
    return sorted(res.entities.values(), key=lambda e: e.order)
