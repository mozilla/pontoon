#
# Copyright 2007-2008 Zuza Software Foundation
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
This module contains all the common features for languages.

Supported features:

- language code (km, af)
- language name (Khmer, Afrikaans)
- Plurals

  - Number of plurals (nplurals)
  - Plural equation

- pofilter tests to ignore

Segmentation:

- characters
- words
- sentences

Punctuation:

- End of sentence
- Start of sentence
- Middle of sentence
- Quotes

  - single
  - double

- Valid characters
- Accelerator characters
- Special characters
- Direction (rtl or ltr)

TODOs and Ideas for possible features:

- Language-Team information
- Segmentation

  - phrases
"""

import logging
import re

from translate.lang import data

logger = logging.getLogger(__name__)


class Common:
    """This class is the common parent class for all language classes."""

    code = ""
    """The ISO 639 language code, possibly with a country specifier or other
    modifier.

    Examples::

        km
        pt_BR
        sr_YU@Latn
    """

    fullname = ""
    """The full (English) name of this language.

    Dialect codes should have the form of:

    - Khmer
    - Portugese (Brazil)
    - TODO: sr_YU@Latn?
    """

    nplurals = 0
    """The number of plural forms of this language.

    0 is not a valid value - it must be overridden.
    Any positive integer is valid (it should probably be between 1 and 6)

    .. seealso:: :mod:`translate.lang.data`
    """

    pluralequation = "0"
    """The plural equation for selection of plural forms.

    This is used for PO files to fill into the header.

    .. seealso::

       `Gettext manual <http://www.gnu.org/software/gettext/manual/html_node/gettext_150.html#Plural-forms>`_, :mod:`translate.lang.data`
    """
    # Don't change these defaults of nplurals or pluralequation willy-nilly:
    # some code probably depends on these for unrecognised languages

    mozilla_nplurals = 0
    mozilla_pluralequation = "0"
    """This of languages that has different plural formula in Mozilla than the
    standard one in Gettext."""

    listseperator = ", "
    """This string is used to separate lists of textual elements. Most
    languages probably can stick with the default comma, but Arabic and some
    Asian languages might want to override this."""

    specialchars = ""
    """Characters used by the language that might not be easy to input with
    common keyboard layouts"""

    commonpunc = ".,;:!?-@#$%^*_()[]{}/\\'`\"<>"
    """These punctuation marks are common in English and most languages that
    use latin script."""

    quotes = "‘’‛“”„‟′″‴‵‶‷‹›«»"
    """These are different quotation marks used by various languages."""

    invertedpunc = "¿¡"
    """Inverted punctuation sometimes used at the beginning of sentences in
    Spanish, Asturian, Galician, and Catalan."""

    rtlpunc = "،؟؛÷"
    """These punctuation marks are used by Arabic and Persian, for example."""

    CJKpunc = "。、，；！？「」『』【】"
    """These punctuation marks are used in certain circumstances with CJK
    languages."""

    indicpunc = "।॥॰"
    """These punctuation marks are used by several Indic languages."""

    ethiopicpunc = "።፤፣"
    """These punctuation marks are used by several Ethiopic languages."""

    miscpunc = "…±°¹²³·©®×£¥€"
    """The middle dot (·) is used by Greek and Georgian."""

    punctuation = f"{commonpunc}{quotes}{invertedpunc}{rtlpunc}{CJKpunc}{indicpunc}{ethiopicpunc}{miscpunc}"
    """We include many types of punctuation here, simply since this is only
    meant to determine if something is punctuation. Hopefully we catch some
    languages which might not be represented with modules. Most languages won't
    need to override this."""

    sentenceend = ".!?…։؟।。！？።\u06d4"
    """These marks can indicate a sentence end. Once again we try to account
    for many languages. Most langauges won't need to override this."""

    # The following tries to account for a lot of things. For the best idea of
    # what works, see test_common.py. We try to ignore abbreviations, for
    # example, by checking that the following sentence doesn't start with lower
    # case or numbers.
    sentencere = re.compile(
        rf"""
        (?s)        # make . also match newlines
        .*?         # anything, but match non-greedy
        [{sentenceend}]        # the puntuation for sentence ending
        \s+         # the spacing after the puntuation
        (?=[^a-zа-џ\d])  # lookahead that next part starts with caps
        """,
        re.VERBOSE | re.UNICODE,
    )

    puncdict = {}
    """A dictionary of punctuation transformation rules that can be used by
    punctranslate()."""

    numbertuple = ()
    """A tuple of number transformation rules that can be used by
    numbertranslate()."""

    ignoretests = {}
    """Dictionary of tests to ignore in some or all checkers.

    Keys are checker names and values are list of names for the ignored tests
    in the checker. A special 'all' checker name can be used to tell that the
    tests must be ignored in all the checkers.

    Listed checkers to ignore tests on must be lowercase strings for the
    checker name, for example "mozilla" for MozillaChecker or "libreoffice" for
    LibreOfficeChecker."""

    checker = None
    """A language specific checker instance (see filters.checks).

    This doesn't need to be supplied, but will be used if it exists."""

    _languages = {}

    validaccel = None
    """Characters that can be used as accelerators (access keys) i.e. Alt+X
    where X is the accelerator.  These can include combining diacritics as
    long as they are accessible from the users keyboard in a single keystroke,
    but normally they would be at least precomposed characters. All characters,
    lower and upper, are included in the list."""

    validdoublewords = []
    """Some languages allow double words in certain cases.  This is a dictionary
    of such words."""

    def __new__(cls, code):
        """
        This returns the language class for the given code, following a
        singleton like approach (only one object per language).
        """
        code = code or ""
        # First see if a language object for this code already exists
        if code in cls._languages:
            return cls._languages[code]
        # No existing language. Let's build a new one and keep a copy
        language = cls._languages[code] = object.__new__(cls)

        language.code = code
        while code:
            langdata = data.get_language(code)
            if langdata:
                language.fullname, language.nplurals, language.pluralequation = langdata
                break
            code = data.simplercode(code)
        return language

    def __deepcopy__(self, memo={}):
        memo[id(self)] = self
        return self

    def __repr__(self):
        """
        Give a simple string representation without address information to
        be able to store it in text for comparison later.
        """
        detail = ""
        if self.code:
            detail = f"({self.code})"
        return f"<class 'translate.lang.common.Common{detail}'>"

    @classmethod
    def numbertranslate(cls, text):
        """
        Converts the numbers in a string according to the rules of the
        language.
        """
        if text:
            for latin_number, native_number in cls.numbertuple:
                text = text.replace(native_number, latin_number)
        return text

    @classmethod
    def punctranslate(cls, text):
        """
        Converts the punctuation in a string according to the rules of the
        language.
        """
        # TODO: look at po::escapeforpo() for performance idea
        if not text:
            return text
        ellipses_end = text.endswith("...")
        if ellipses_end:
            text = text[:-3]
        for source, target in cls.puncdict.items():
            text = text.replace(source, target)
        if ellipses_end:
            if "..." in cls.puncdict:
                text += cls.puncdict["..."]
            else:
                text += "..."
        # Let's account for cases where a punctuation symbol plus a space is
        # replaced, but the space won't exist at the end of the source message.
        # As a simple improvement for messages ending in ellipses (...), we
        # test that the last character is different from the second last
        # This is only relevant if the string has two characters or more
        if (text[-1] + " " in cls.puncdict) and (len(text) < 2 or text[-2] != text[-1]):
            text = text[:-1] + cls.puncdict[text[-1] + " "].rstrip()
        return text

    @classmethod
    def length_difference(cls, length):
        """
        Returns an estimate to a likely change in length relative to an
        English string of length length.
        """
        # This is just a rudimentary heuristic guessing that most translations
        # will be somewhat longer than the source language
        expansion_factor = 0
        code = cls.code
        while code:
            expansion_factor = data.expansion_factors.get(cls.code, 0)
            if expansion_factor:
                break
            code = data.simplercode(code)
        else:
            expansion_factor = 0.1  # default
        constant = max(5, int(40 * expansion_factor))
        # The default: return 5 + length/10
        return constant + int(expansion_factor * length)

    @classmethod
    def alter_length(cls, text):
        """
        Converts the given string by adding or removing characters as an
        estimation of translation length (with English assumed as source
        language).
        """

        def alter_it(text):
            l = len(text)
            if l > 9:
                extra = cls.length_difference(l)
                if extra > 0:
                    text = text[:extra].replace("\n", "") + text
                else:
                    text = text[-extra:]
            return text

        expanded = [alter_it(subtext) for subtext in text.split("\n\n")]
        return "\n\n".join(expanded)

    @classmethod
    def character_iter(cls, text):
        """Returns an iterator over the characters in text."""
        # We don't return more than one consecutive whitespace character
        prev = "A"
        for c in text:
            if c.isspace() and prev.isspace():
                continue
            prev = c
            if c not in cls.punctuation:
                yield c

    @classmethod
    def characters(cls, text):
        """Returns a list of characters in text."""
        return list(cls.character_iter(text))

    @classmethod
    def word_iter(cls, text):
        """Returns an iterator over the words in text."""
        # TODO: Consider replacing puctuation with space before split()
        for w in text.split():
            word = w.strip(cls.punctuation)
            if word:
                yield word

    @classmethod
    def words(cls, text):
        """Returns a list of words in text."""
        return list(cls.word_iter(text))

    @classmethod
    def sentence_iter(cls, text, strip=True):
        """Returns an iterator over the sentences in text."""
        lastmatch = 0
        text = text or ""
        for item in cls.sentencere.finditer(text):
            lastmatch = item.end()
            sentence = item.group()
            if strip:
                sentence = sentence.strip()
            if sentence:
                yield sentence
        remainder = text[lastmatch:]
        if strip:
            remainder = remainder.strip()
        if remainder:
            yield remainder

    @classmethod
    def sentences(cls, text, strip=True):
        """Returns a list of sentences in text."""
        return list(cls.sentence_iter(text, strip=strip))

    @classmethod
    def capsstart(cls, text):
        """Determines whether the text starts with a capital letter."""
        stripped = text.lstrip().lstrip(cls.punctuation)
        return stripped and stripped[0].isupper()

    @classmethod
    def numstart(cls, text):
        """Determines whether the text starts with a numeric value."""
        stripped = text.lstrip().lstrip(cls.punctuation)
        return stripped and stripped[0].isnumeric()
