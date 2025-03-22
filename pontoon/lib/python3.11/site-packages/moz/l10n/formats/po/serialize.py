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

from collections.abc import Iterator
from re import match

from polib import POEntry, POFile

from ...model import Entry, Message, PatternMessage, Resource, SelectMessage


def po_serialize(
    resource: Resource[str] | Resource[Message],
    trim_comments: bool = False,
    wrapwidth: int = 200,
) -> Iterator[str]:
    """
    Serialize a resource as the contents of a .po file.

    Section identifiers are not supported.
    Message identifiers may have one or two parts,
    with the second one holding the optional message context.
    Comments and metadata on sections is not supported.

    Yields each entry and empty line separately.
    """

    pf = POFile(wrapwidth=wrapwidth)
    if not trim_comments and resource.comment and not resource.comment.isspace():
        pf.header = resource.comment.rstrip() + "\n"
    pf.metadata = {m.key: m.value for m in resource.meta}
    yield str(pf)

    nplurals = 1
    plural_forms = pf.metadata.get("Plural-Forms", None)
    if isinstance(plural_forms, str):
        pm = match(r"\s*nplurals=(\d+);", plural_forms)
        if pm is not None:
            nplurals = int(pm[1])

    for section in resource.sections:
        if section.comment:
            raise ValueError("Section comments are not supported")
        if section.meta:
            raise ValueError("Section metadata is not supported")
        for entry in section.entries:
            if isinstance(entry, Entry):
                context = entry.id[1] if len(entry.id) == 2 else None
                pe = POEntry(msgctxt=context, msgid=entry.id[0])
                msg = entry.value
                if isinstance(msg, str):
                    pe.msgstr = msg
                elif isinstance(msg, PatternMessage) and all(
                    isinstance(p, str) for p in msg.pattern
                ):
                    pe.msgstr = "".join(msg.pattern)  # type: ignore[arg-type]
                elif (
                    isinstance(msg, SelectMessage)
                    and len(msg.declarations) == 1
                    and len(msg.selectors) == 1
                    and (sel := msg.selector_expressions()[0])
                    and sel.function == "number"
                    and not sel.options
                    and all(
                        len(keys) == 1 and all(isinstance(p, str) for p in pattern)
                        for keys, pattern in msg.variants.items()
                    )
                ):
                    pe.msgstr_plural = {
                        idx: next(
                            (
                                "".join(pattern)  # type: ignore[arg-type]
                                for keys, pattern in msg.variants.items()
                                if (
                                    key
                                    if isinstance(key := keys[0], str)
                                    else key.value
                                )
                                == str(idx)
                            ),
                            "",
                        )
                        for idx in range(nplurals)
                    }
                else:
                    raise ValueError(
                        f"Value for {entry.id} is not supported: {entry.value}"
                    )
                if not trim_comments:
                    pe.tcomment = entry.comment.rstrip()
                for m in entry.meta:
                    if m.key == "obsolete":
                        pe.obsolete = m.value != "false"
                    elif m.key == "plural":
                        pe.msgid_plural = m.value
                    elif not trim_comments:
                        if m.key == "translator-comments":
                            cs = (m.value).lstrip("\n").rstrip()
                            pe.tcomment = f"{pe.tcomment}\n{cs}" if pe.tcomment else cs
                        elif m.key == "extracted-comments":
                            pe.comment = (m.value).lstrip("\n").rstrip()
                        elif m.key == "reference":
                            pos = m.value.split(":", 1)
                            pe.occurrences.append(
                                (pos[0], pos[1]) if len(pos) == 2 else (m.value, "")
                            )
                        elif m.key == "flag":
                            pe.flags.append(m.value)
                        else:
                            raise ValueError(
                                f'Unsupported meta entry "{m.key}" for {entry.id}: {m.value}'
                            )
                if not pe.obsolete or not trim_comments:
                    yield "\n"
                    yield pe.__unicode__(wrapwidth=wrapwidth)
            else:
                raise ValueError(
                    f"Standalone comments are not supported: {entry.comment}"
                )
