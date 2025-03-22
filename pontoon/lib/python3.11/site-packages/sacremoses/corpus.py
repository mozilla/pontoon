#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import pkgutil


class Perluniprops:
    """
    This class is used to read lists of characters from the Perl Unicode
    Properties (see http://perldoc.perl.org/perluniprops.html).
    The files in the perluniprop.zip are extracted using the Unicode::Tussle
    module from http://search.cpan.org/~bdfoy/Unicode-Tussle-1.11/lib/Unicode/Tussle.pm
    """

    def __init__(self):
        self.datadir = (
            os.path.dirname(os.path.abspath(__file__)) + "/data/perluniprops/"
        )
        # These are categories similar to the Perl Unicode Properties
        self.available_categories = [
            "Close_Punctuation",
            "Currency_Symbol",
            "IsAlnum",
            "IsAlpha",
            "IsLower",
            "IsN",
            "IsSc",
            "IsSo",
            "IsUpper",
            "Line_Separator",
            "Number",
            "Open_Punctuation",
            "Punctuation",
            "Separator",
            "Symbol",
            "Lowercase_Letter",
            "Titlecase_Letter",
            "Uppercase_Letter",
            "IsPf",
            "IsPi",
            "CJKSymbols",
            "CJK",
        ]

    def chars(self, category=None):
        """
        This module returns a list of characters from  the Perl Unicode Properties.
        They are very useful when porting Perl tokenizers to Python.

            >>> from sacremoses.corpus import Perluniprops
            >>> pup = Perluniprops()
            >>> list(pup.chars('Open_Punctuation'))[:5] == ['(', '[', '{', '\u0f3a', '\u0f3c']
            True
            >>> list(pup.chars('Currency_Symbol'))[:5] == ['$', '\xa2', '\xa3', '\xa4', '\xa5']
            True
            >>> pup.available_categories[:5]
            ['Close_Punctuation', 'Currency_Symbol', 'IsAlnum', 'IsAlpha', 'IsLower']

        :return: a generator of characters given the specific unicode character category
        """
        relative_path = os.path.join("data", "perluniprops", category + ".txt")
        binary_data = pkgutil.get_data("sacremoses", relative_path)
        for ch in binary_data.decode("utf-8"):
            yield ch


class NonbreakingPrefixes:
    """
    This is a class to read the nonbreaking prefixes textfiles from the
    Moses Machine Translation toolkit. These lists are used in the Python port
    of the Moses' word tokenizer.
    """

    def __init__(self):
        self.datadir = (
            os.path.dirname(os.path.abspath(__file__)) + "/data/nonbreaking_prefixes/"
        )
        self.available_langs = {
            "assamese": "as",
            "bengali": "bn",
            "catalan": "ca",
            "czech": "cs",
            "german": "de",
            "greek": "el",
            "english": "en",
            "spanish": "es",
            "estonian": "et",
            "finnish": "fi",
            "french": "fr",
            "irish": "ga",
            "gujarati": "gu",
            "hindi": "hi",
            "hungarian": "hu",
            "icelandic": "is",
            "italian": "it",
            "kannada": "kn",
            "lithuanian": "lt",
            "latvian": "lv",
            "malayalam": "ml",
            "manipuri": "mni",
            "marathi": "mr",
            "dutch": "nl",
            "oriya": "or",
            "punjabi": "pa",
            "polish": "pl",
            "portuguese": "pt",
            "romanian": "ro",
            "russian": "ru",
            "slovak": "sk",
            "slovenian": "sl",
            "swedish": "sv",
            "tamil": "ta",
            "telugu": "te",
            "tetum": "tdt",
            "cantonese": "yue",
            "chinese": "zh",
        }
        # Also, add the lang IDs as the keys.
        self.available_langs.update({v: v for v in self.available_langs.values()})

    def words(self, lang=None, ignore_lines_startswith="#"):
        """
        This module returns a list of nonbreaking prefixes for the specified
        language(s).

            >>> from sacremoses.corpus import NonbreakingPrefixes
            >>> nbp = NonbreakingPrefixes()
            >>> list(nbp.words('en'))[:10] == ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
            True
            >>> list(nbp.words('ta'))[:5] == ['\u0bb0', '\u0bc2', '\u0ba4\u0bbf\u0bb0\u0bc1', '\u0b8f', '\u0baa\u0bc0']
            True

        :return: a generator words for the specified language(s).
        """
        # If *lang* in list of languages available, allocate apt fileid.
        if lang in self.available_langs:
            filenames = ["nonbreaking_prefix." + self.available_langs[lang]]
        # Use non-breaking prefixes for all languages when lang==None.
        elif lang == None:
            filenames = [
                "nonbreaking_prefix." + v for v in set(self.available_langs.values())
            ]
        else:
            filenames = ["nonbreaking_prefix.en"]

        for filename in filenames:
            relative_path = os.path.join("data", "nonbreaking_prefixes", filename)
            binary_data = pkgutil.get_data("sacremoses", relative_path)
            for line in binary_data.decode("utf-8").splitlines():
                line = line.strip()
                if line and not line.startswith(ignore_lines_startswith):
                    yield line


__all__ = ["Perluniprops", "NonbreakingPrefixes"]
