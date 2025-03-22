#
# Copyright 2007-2017 Zuza Software Foundation
#
# This file is part of the Translate Toolkit.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

"""
This module represents the Romanian language.

.. seealso:: :wp:`Romanian_language`
"""

from translate.filters.checks import FilterFailure, TranslationChecker
from translate.filters.decorators import cosmetic
from translate.lang import common


def contains_illegal(illegal_substrings, string):
    """
    Check if string contains any of the specified illegal substrings.

    :param illegal_substrings: an iterable of illegal substrings
    :param string: the string to check against occurences of illegal substrings
    :return: True if string contains any of the illegal substrings
    """
    return any(s in string for s in illegal_substrings)


class RomanianChecker(TranslationChecker):
    """A Checker class for Romanian."""

    @cosmetic
    def cedillas(self, str1, str2):
        """
        Check if the translation contains an illegal cedilla character.

        Cedillas are obsoleted diacritics for Romanian:

          - U+0162 Latin capital letter T with cedilla
          - U+0163 Latin small letter T with cedilla
          - U+015E Latin capital letter S with cedilla
          - U+015F Latin small letter S with cedilla

        Cedilla-letters are only valid for Turkish (S-cedilla) and Gagauz
        languages (S-cedilla and T-comma). Fun fact: Gagauz is the only known
        language to use T-cedilla.

        :param str1: the source string
        :param str2: the target (translated) string
        :return: True if str2 contains a cedilla character
        """
        if contains_illegal(["Ţ", "Ş", "ţ", "ş"], str2):
            raise FilterFailure("String contains illegal cedillas")
        return True

    @cosmetic
    def niciun_nicio(self, str1, str2):
        """
        Checks for sequences containing 'nici un'/'nici o' which are obsolete
        Romanian syntax. Correct is 'niciun'/'nicio'.
        """
        if contains_illegal(["nici un", "nici o"], str2):
            raise FilterFailure("String contains 'nici un' or 'nici o'")
        return True


class ro(common.Common):
    """This class represents Romanian."""

    checker = RomanianChecker()
