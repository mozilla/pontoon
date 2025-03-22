#
# Copyright 2019 Cademia Siciliana <tech@cademiasiciliana.org>
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
This module represents the Sicilian language.

.. seealso:: :wp:`Sicilian_language`
"""

from translate.filters.checks import CheckerConfig, FilterFailure, TranslationChecker
from translate.filters.decorators import critical
from translate.lang import common


def contains_illegal(illegal_substrings, string):
    """
    Check if string contains any of the specified illegal substrings.

    :param illegal_substrings: an iterable of illegal substrings
    :param string: the string to check against occurences of illegal substrings
    :return: True if string contains any of the illegal substrings
    """
    return any(s in string for s in illegal_substrings)


sicilianconfig = CheckerConfig(
    validchars="àèìòùḍÀÈÌÒÙḌ",
)


class SicilianChecker(TranslationChecker):
    """A Checker class for Sicilian."""

    def __init__(self, **kwargs):
        checkerconfig = kwargs.get("checkerconfig")

        if checkerconfig is None:
            checkerconfig = CheckerConfig()
            kwargs["checkerconfig"] = checkerconfig

        checkerconfig.update(sicilianconfig)
        super().__init__(**kwargs)

    @critical
    def italianisms(self, str1, str2):
        """
        Check if the translation contains common errors done by italophones.

        Mainly inspired by musttranslatewords(), but with a different logic: return True if
        the given word appears in the translation but not in the source (if it's in the source,
        then presumably it's being kept untranslated).

        :param str1: the source string
        :param str2: the target (translated) string
        :return: True if str2 doesn't contain an "italianism"
        """
        str1 = self.removevariables(str1)
        str2 = self.removevariables(str2)

        errors = {
            "io": "ju/jeu/iu/...",
            "tantu": "assai",
            "menu": "cchiù picca",
        }

        # The above is full of strange quotes and things in utf-8 encoding.
        # single apostrophe perhaps problematic in words like "doesn't"
        for separator in self.config.punctuation:
            str1 = str1.replace(separator, " ")
            str2 = str2.replace(separator, " ")

        words1 = self.filteraccelerators(str1).split()
        words2 = self.filteraccelerators(str2).split()
        stopwords = [
            f"{word} ({errors[word]})"
            for word in words2
            if word.lower() in errors and word not in words1
        ]

        if stopwords:
            raise FilterFailure("Please translate: {}".format(", ".join(stopwords)))

        return True

    @critical
    def vocalism(self, str1, str2):
        """
        Check correct word-endings.

        All words should end with a/i/u, but a handful of exceptions:

          - me, to, so (possessive pronouns)
          - po (verb "putiri")
          - no
          - jo (personal pronoun)
          - se (yes)
          - nne (in)

        :param str1: the source string
        :param str2: the target (translated) string
        :return: True if there are no words with endings not in respect of vocalism (or if they appear in source string as well)
        """
        exceptions = ["me", "to", "so", "po", "no", "jo", "se", "nne"]

        stopwords = []

        for word in self.config.lang.words(str2):
            lower_word = word.lower()
            if (
                word not in str1
                and lower_word not in exceptions
                and lower_word.endswith(("e", "o"))
                and lower_word not in stopwords
            ):
                stopwords.append(lower_word)

        if stopwords:
            raise FilterFailure(
                "Please respect vocalism: {}".format(", ".join(stopwords))
            )
        return True

    @critical
    def suffixes(self, str1, str2):
        """
        Check for common word suffixes to be written correctly.

        :param str1: the source string
        :param str2: the target (translated) string
        :return: True if there are no common suffixes wrongly written
        """
        suffixes = {
            "zzioni": "zziuni",
        }

        stopwords = [
            f"{word} (-{suffixes[suffix]})"
            for word in self.config.lang.words(str2)
            for suffix in suffixes
            if word not in str1 and word.lower().endswith(suffix)
        ]

        if stopwords:
            raise FilterFailure(
                "Please use the correct word endings: {}".format(", ".join(stopwords))
            )
        return True


class scn(common.Common):
    """This class represents Sicilian."""

    checker = SicilianChecker()

    ignoretests = {
        "all": ["doublewords"],
    }
