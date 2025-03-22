from functools import lru_cache

import regex

from .tokenizer_base import BaseTokenizer


class TokenizerV14International(BaseTokenizer):
    """Tokenizes a string following the official BLEU implementation.

    See github.com/moses-smt/mosesdecoder/blob/master/scripts/generic/mteval-v14.pl#L954-L983

    In our case, the input string is expected to be just one line.
    We just tokenize on punctuation and symbols,
    except when a punctuation is preceded and followed by a digit
    (e.g. a comma/dot as a thousand/decimal separator).
    We do not recover escaped forms of punctuations such as &apos; or &gt;
    as these should never appear in MT system outputs (see issue #138)

    Note that a number (e.g., a year) followed by a dot at the end of
    sentence is NOT tokenized, i.e. the dot stays with the number because
    `s/(\\p{P})(\\P{N})/ $1 $2/g` does not match this case (unless we add a
    space after each sentence). However, this error is already in the
    original mteval-v14.pl and we want to be consistent with it.
    The error is not present in the non-international version,
    which uses `$norm_text = " $norm_text "`.

    :param line: the input string to tokenize.
    :return: The tokenized string.
    """

    def signature(self):
        return 'intl'

    def __init__(self):
        self._re = [
            # Separate out punctuations preceeded by a non-digit
            (regex.compile(r'(\P{N})(\p{P})'), r'\1 \2 '),
            # Separate out punctuations followed by a non-digit
            (regex.compile(r'(\p{P})(\P{N})'), r' \1 \2'),
            # Separate out symbols
            (regex.compile(r'(\p{S})'), r' \1 '),
        ]

    @lru_cache(maxsize=2**16)
    def __call__(self, line: str) -> str:
        for (_re, repl) in self._re:
            line = _re.sub(repl, line)

        return ' '.join(line.split())
