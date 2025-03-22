from functools import lru_cache
import re

from .tokenizer_base import BaseTokenizer


class TokenizerRegexp(BaseTokenizer):

    def signature(self):
        return 're'

    def __init__(self):
        self._re = [
            # language-dependent part (assuming Western languages)
            (re.compile(r'([\{-\~\[-\` -\&\(-\+\:-\@\/])'), r' \1 '),
            # tokenize period and comma unless preceded by a digit
            (re.compile(r'([^0-9])([\.,])'), r'\1 \2 '),
            # tokenize period and comma unless followed by a digit
            (re.compile(r'([\.,])([^0-9])'), r' \1 \2'),
            # tokenize dash when preceded by a digit
            (re.compile(r'([0-9])(-)'), r'\1 \2 '),
            # one space only between words
            # NOTE: Doing this in Python (below) is faster
            # (re.compile(r'\s+'), r' '),
        ]

    @lru_cache(maxsize=2**16)
    def __call__(self, line):
        """Common post-processing tokenizer for `13a` and `zh` tokenizers.

        :param line: a segment to tokenize
        :return: the tokenized line
        """
        for (_re, repl) in self._re:
            line = _re.sub(repl, line)

        # no leading or trailing spaces, single space within words
        return ' '.join(line.split())
