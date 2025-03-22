# Copyright 2002, 2003 St James Software
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
Implements a case-insensitive (on keys) dictionary and order-sensitive
dictionary.
"""


class cidict(dict):
    def __getitem__(self, key):
        if not isinstance(key, str):
            raise TypeError(
                f"cidict can only have str or unicode as key (got {type(key)!r})"
            )
        lkey = key.lower()
        for akey in self.keys():
            if akey.lower() == lkey:
                return super().__getitem__(akey)
        raise IndexError

    def __setitem__(self, key, value):
        if not isinstance(key, str):
            raise TypeError(
                f"cidict can only have str or unicode as key (got {type(key)!r})"
            )
        lkey = key.lower()
        for akey in self.keys():
            if akey.lower() == lkey:
                return super().__setitem__(akey, value)
        return super().__setitem__(key, value)

    def __delitem__(self, key):
        if not isinstance(key, str):
            raise TypeError(
                f"cidict can only have str or unicode as key (got {type(key)!r})"
            )
        lkey = key.lower()
        for akey in self.keys():
            if akey.lower() == lkey:
                return super().__delitem__(akey)
        raise IndexError

    def __contains__(self, key):
        if not isinstance(key, str):
            raise TypeError(
                f"cidict can only have str or unicode as key (got {type(key)!r})"
            )
        lkey = key.lower()
        return any(akey.lower() == lkey for akey in self.keys())
