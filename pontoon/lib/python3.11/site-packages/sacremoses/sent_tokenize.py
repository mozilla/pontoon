#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

from sacremoses.corpus import Perluniprops
from sacremoses.corpus import NonbreakingPrefixes

perluniprops = Perluniprops()
nonbreaking_prefixes = NonbreakingPrefixes()


class MosesSentTokenizer(object):
    """
    This is a Python port of the Moses Tokenizer from
    https://github.com/moses-smt/mosesdecoder/blob/master/scripts/ems/support/split-sentences.perl
    """

    raise NotImplementedError

    r"""
    # Perl Unicode Properties character sets.
    IsPi = str("".join(perluniprops.chars("IsPi")))
    IsUpper = str("".join(perluniprops.chars("IsUpper")))
    IsPf = str("".join(perluniprops.chars("IsPf")))
    Punctuation = str("".join(perluniprops.chars("Punctuation")))
    CJK = str("".join(perluniprops.chars("CJK")))
    CJKSymbols = str("".join(perluniprops.chars("CJKSymbols")))
    IsAlnum = str("".join(perluniprops.chars("IsAlnum")))

    # Remove ASCII junk.
    DEDUPLICATE_SPACE = r"\s+", r" "

    # Non-period end of sentence markers (?!) followed by sentence starters.
    NONPERIOD_UPPER = r"([?!]) +([\'\"\(\[\¿\¡\p{startpunct}]*[\p{upper}])".format(startpunct=IsPi, upper=IsUpper), r"\1\n\2"

    # Multi-dots followed by sentence starters.
    MULTDOT_UPPER = r"(\.[\.]+) +([\'\"\(\[\¿\¡\p{startpunct}]*[\p{upper}])".format(startpunct=IsPi, upper=IsUpper), r"\1\n\2"

    # Add breaks for sentences that end with some sort of punctuation
    # inside a quote or parenthetical and are followed by a possible
    # sentence starter punctuation and upper case.
    QUOTES_UPPER = r"([?!\.][\ ]*[\'\"\)\]\p{endpunct}]+) +([\'\"\(\[\¿\¡\p{startpunct}]*[\ ]*[\p{upper}])".format(endpunct=IsPf, startpunct=IsPi, upper=IsUpper), r"\1\n\2"

    # Add breaks for sentences that end with some sort of punctuation,
    # and are followed by a sentence starter punctuation and upper case.
    ENDPUNCT_UPPER = r"([?!\.]) +([\'\"\(\[\¿\¡\p{startpunct}]+[\ ]*[\p{upper}])".format(startpunct=IsPi, upper=IsUpper), r"\1\n\2"

    IS_EOS = r"([\p{alphanum}\.\-]*)([\'\"\)\]\%\p{endpunct}]*)(\.+)$".format(alphanum=IsAlnum, endpunct=IsPf)


    def __init__(self, lang="en", custom_nonbreaking_prefixes_file=None):
        # Load custom nonbreaking prefixes file.
        if custom_nonbreaking_prefixes_file:
            self.NONBREAKING_PREFIXES  = []
            with open(custom_nonbreaking_prefixes_file, 'r') as fin:
                for line in fin:
                    line = line.strip()
                    if line and not line.startswith("#"):
                        if line not in self.NONBREAKING_PREFIXES:
                            self.NONBREAKING_PREFIXES.append(line)

        detokenized_text = ""
        tokens = text.split()
        # Iterate through every token till the last 2nd token.
        for i, token in enumerate(iter(tokens[:-1])):
            if re.search(IS_EOS, token):
                pass
    """
