#
# Copyright 2006 Zuza Software Foundation
#
# This file is part of translate.
#
# translate is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# translate is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""
Supports a hybrid Unicode string that can also have a list of alternate
strings in the strings attribute.
"""

from __future__ import annotations


class multistring(str):
    def __new__(cls, string: list[str] | str | None = None):
        if string is None:
            string = [""]
        elif isinstance(string, str):
            string = [string]
        if not isinstance(string, list) or any(
            not isinstance(value, str) for value in string
        ):
            raise TypeError("multistring can only contain strings or list of strings")
        if not string:
            raise ValueError("multistring must contain at least one string")

        newstring = str.__new__(cls, string[0])
        newstring.extra_strings = string[1:]
        return newstring

    def __init__(self, *args, **kwargs):
        super().__init__()
        if not hasattr(self, "extra_strings"):
            self.extra_strings = []

    @property
    def strings(self) -> list[str]:
        return [self, *self.extra_strings]

    def __hash__(self) -> int:
        return super().__hash__()

    def __ne__(self, other) -> bool:
        return not self.__eq__(other)

    def __eq__(self, other) -> bool:
        if isinstance(other, multistring):
            return super().__eq__(other) and self.extra_strings == other.extra_strings
        if isinstance(other, str):
            return super().__eq__(other)
        if isinstance(other, list):
            return self.strings == other
        return super().__eq__(other)

    def __repr__(self) -> str:
        strings = [str(self), *self.extra_strings]
        return f"multistring({strings!r})"

    def replace(self, old: str, new: str, count: int = -1) -> multistring:
        newstr = multistring(super().replace(old, new, count))
        newstr.extra_strings.extend(
            s.replace(old, new, count) for s in self.extra_strings
        )
        return newstr
