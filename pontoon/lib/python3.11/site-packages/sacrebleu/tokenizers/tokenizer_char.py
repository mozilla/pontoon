from functools import lru_cache
from .tokenizer_base import BaseTokenizer


class TokenizerChar(BaseTokenizer):
    def signature(self):
        return 'char'

    def __init__(self):
        pass

    @lru_cache(maxsize=2**16)
    def __call__(self, line):
        """Tokenizes all the characters in the input line.

        :param line: a segment to tokenize
        :return: the tokenized line
        """
        return " ".join((char for char in line))
