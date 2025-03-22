import os
import plistlib
import re

from translate.lang import data
from translate.misc.multistring import multistring
from translate.storage import base


class StringsDictId(base.UnitId):
    KEY_SEPARATOR = ":"

    def __str__(self):
        s = super().__str__()
        if s.startswith(":"):
            return s[1:]
        return s


class StringsDictUnit(base.DictUnit):
    """
    A single entry in a .stringsdict file.
    One entry represents either a localized format string, or a variable used
    within another string.
    """

    IdClass = StringsDictId
    format_value_type = ""

    def __init__(self, source=None):
        super().__init__(source=source)

        loc = source or ""
        if len(loc) > 0 and loc[0] == ":":
            loc = loc[1:]

        # Check if this unit is a format string or a variable
        split = loc.rfind(":")
        if split > 0:
            subkey = loc[(split + 1) :]
            loc = loc[:split]
            self.set_unitid(self.IdClass([("key", loc), ("key", subkey)]))
        else:
            self.set_unitid(self.IdClass([("key", loc)]))

    def __eq__(self, other):
        return (
            super().__eq__(other) and self.format_value_type == other.format_value_type
        )

    @property
    def outerkey(self):
        self.get_unitid()

        if len(self._unitid.parts) < 1:
            return None

        return self._unitid.parts[0][1]

    @property
    def innerkey(self):
        self.get_unitid()

        if len(self._unitid.parts) < 2:
            return None

        return self._unitid.parts[1][1]

    def getid(self):
        return self.source

    def setid(self, value, unitid=None):
        self.source = value
        super().setid(value, unitid)


class StringsDictFile(base.DictStore):
    """
    Class representing a .stringsdict file.

    One entry in a .stringsdict file consists of a format string, and any
    number of variables with plural strings.

    Each entry is split up into multiple translation units, containing either
    the format string or one of the variables.
    """

    UnitClass = StringsDictUnit
    Name = "iOS Stringsdict"
    Mimetypes = ["application/x-plist"]
    Extensions = ["stringsdict"]

    def __init__(self, inputfile=None, **kwargs):
        super().__init__(**kwargs)
        self.parse(inputfile)

    def gettargetlanguage(self):
        target_lang = super().gettargetlanguage()

        # If targetlanguage isn't set, we try to extract it from the filename path (if any).
        if target_lang is None and hasattr(self, "filename") and self.filename:
            parent_dir = os.path.split(os.path.dirname(self.filename))[1]
            match = re.search(r"^(\w*).lproj", parent_dir)
            if match is not None:
                target_lang = match.group(1)
                if target_lang.lower() == "base":
                    target_lang = "en"
            else:
                target_lang = self.sourcelanguage

            # Cache it
            self.settargetlanguage(target_lang)

        return target_lang

    @property
    def target_plural_tags(self):
        """
        Get all supported plural tags for the target language.
        Note that 'zero' is always supported.
        """
        target_lang = self.gettargetlanguage()
        if target_lang is None:
            return data.cldr_plural_categories

        locale = target_lang.replace("_", "-").split("-")[0]
        tags = data.plural_tags.get(locale, data.cldr_plural_categories).copy()
        if "zero" not in tags:
            tags.insert(0, "zero")
        return tags

    def parse(self, input):
        """Read a .stringsdict file into a dictionary, and convert it to translation units."""
        if isinstance(input, (bytes, str)):
            plist = plistlib.loads(input)
        elif input is not None:
            plist = plistlib.load(input)
        else:
            plist = {}

        for key, outer in plist.items():
            if not isinstance(outer, dict):
                raise TypeError(f"{key} is not a dict")
            for innerkey, value in outer.items():
                if innerkey == "NSStringLocalizedFormatKey":
                    u = self.UnitClass()
                    u.set_unitid(u.IdClass([("key", key)]))
                    u.target = str(value)
                    self.addunit(u)
                elif isinstance(value, dict):
                    spec_type = value.get("NSStringFormatSpecTypeKey", "")
                    if spec_type and spec_type != "NSStringPluralRuleType":
                        raise ValueError(
                            f"{innerkey} in {key} is not of NSStringPluralRuleType"
                        )

                    plural_tags = self.target_plural_tags
                    plural_strings = [value.get(tag, "") for tag in plural_tags]

                    u = self.UnitClass()
                    u.set_unitid(u.IdClass([("key", key), ("key", innerkey)]))
                    u.target = multistring(plural_strings)
                    u.format_value_type = value.get("NSStringFormatValueTypeKey", "")
                    self.addunit(u)
                else:
                    raise ValueError(f"Unexpected key {innerkey} in {key}")

    def serialize(self, out):
        plist = {}

        for u in self.units:
            loc = u.outerkey
            subkey = u.innerkey

            if loc not in plist:
                plist[loc] = {}

            if subkey is not None:
                plurals = {}
                plurals["NSStringFormatSpecTypeKey"] = "NSStringPluralRuleType"
                plurals["NSStringFormatValueTypeKey"] = u.format_value_type

                plural_tags = self.target_plural_tags

                # Sync plural_strings elements to plural_tags count.
                plural_strings = self.UnitClass.sync_plural_count(u.target, plural_tags)
                plurals.update(
                    (plural_tag, plural_string)
                    for plural_tag, plural_string in zip(plural_tags, plural_strings)
                    if plural_string
                )

                plist[loc][subkey] = plurals
            else:
                plist[loc]["NSStringLocalizedFormatKey"] = u.target or u.source

        out.write(plistlib.dumps(plist, sort_keys=False))
