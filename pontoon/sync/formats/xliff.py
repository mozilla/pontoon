"""
Parser for the xliff translation format.
"""

from __future__ import annotations

from lxml import etree

from translate.storage import xliff

from .common import ParseError, VCSTranslation


def parse_xml_unit(unit: xliff.xliffunit, order: int):
    key = unit.getid()
    rich_target = unit.get_rich_target()
    target_string = str(rich_target[0]) if rich_target else None
    notes = unit.getnotes()
    return VCSTranslation(
        key=key,
        context=unit.xmlelement.get("id"),
        order=order,
        strings={None: target_string} if target_string else {},
        source_string=str(unit.rich_source[0]),
        comments=notes.split("\n") if notes else None,
    )


def parse(path: str):
    try:
        with open(path) as f:
            xml = f.read().encode("utf-8")
            xliff_file = xliff.xlifffile(xml)
            return [
                parse_xml_unit(unit, order)
                for order, unit in enumerate(xliff_file.units)
            ]
    except (OSError, etree.XMLSyntaxError) as err:
        raise ParseError(f"Failed to parse {path}: {err}")
