# Copyright Mozilla Foundation
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from __future__ import annotations

from polib import pofile

from ...model import (
    CatchallKey,
    Comment,
    Entry,
    Expression,
    Message,
    Metadata,
    PatternMessage,
    Resource,
    Section,
    SelectMessage,
    VariableRef,
)
from .. import Format


def po_parse(source: str | bytes) -> Resource[Message]:
    """
    Parse a .po or .pot file into a message resource

    Message identifiers may have one or two parts,
    with the second one holding the optional message context.

    Messages may include the following metadata:
    - `translator-comments`
    - `extracted-comments`
    - `reference`: `f"{file}:{line}"`, separately for each reference
    - `obsolete`: `""`
    - `flag`: separately for each flag
    - `plural`
    """
    pf = pofile(source if isinstance(source, str) else source.decode())
    res_comment = pf.header.lstrip("\n").rstrip()
    res_meta: list[Metadata] = [
        Metadata(key, value.strip()) for key, value in pf.metadata.items()
    ]
    entries: list[Entry[Message] | Comment] = []
    for pe in pf:
        meta: list[Metadata] = []
        if pe.tcomment:
            meta.append(Metadata("translator-comments", pe.tcomment))
        if pe.comment:
            meta.append(Metadata("extracted-comments", pe.comment))
        for file, line in pe.occurrences:
            meta.append(Metadata("reference", f"{file}:{line}"))
        if pe.obsolete:
            meta.append(Metadata("obsolete", "true"))
        for flag in pe.flags:
            meta.append(Metadata("flag", flag))
        if pe.msgid_plural:
            meta.append(Metadata("plural", pe.msgid_plural))
        if pe.msgstr_plural:
            keys = list(pe.msgstr_plural)
            keys.sort()
            sel = Expression(VariableRef("n"), "number")
            max_idx = keys[-1]
            value: Message = SelectMessage(
                declarations={"n": sel},
                selectors=(VariableRef("n"),),
                variants={
                    (str(idx) if idx < max_idx else CatchallKey(str(idx)),): (
                        [pe.msgstr_plural[idx]] if idx in pe.msgstr_plural else []
                    )
                    for idx in range(max_idx + 1)
                },
            )
        else:
            value = PatternMessage([pe.msgstr])
        id = (pe.msgid, pe.msgctxt) if pe.msgctxt else (pe.msgid,)
        entries.append(Entry(id, value, meta=meta))
    return Resource(Format.po, [Section((), entries)], res_comment, res_meta)
