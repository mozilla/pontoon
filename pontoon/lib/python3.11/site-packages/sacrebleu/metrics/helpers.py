"""Various utility functions for word and character n-gram extraction."""

from collections import Counter
from typing import List, Tuple


def extract_all_word_ngrams(line: str, min_order: int, max_order: int) -> Tuple[Counter, int]:
    """Extracts all ngrams (min_order <= n <= max_order) from a sentence.

    :param line: A string sentence.
    :param min_order: Minimum n-gram order.
    :param max_order: Maximum n-gram order.
    :return: a Counter object with n-grams counts and the sequence length.
    """

    ngrams = []
    tokens = line.split()

    for n in range(min_order, max_order + 1):
        for i in range(0, len(tokens) - n + 1):
            ngrams.append(tuple(tokens[i: i + n]))

    return Counter(ngrams), len(tokens)


def extract_word_ngrams(tokens: List[str], n: int) -> Counter:
    """Extracts n-grams with order `n` from a list of tokens.

    :param tokens: A list of tokens.
    :param n: The order of n-grams.
    :return: a Counter object with n-grams counts.
    """
    return Counter([' '.join(tokens[i:i + n]) for i in range(len(tokens) - n + 1)])


def extract_char_ngrams(line: str, n: int, include_whitespace: bool = False) -> Counter:
    """Yields counts of character n-grams from a sentence.

    :param line: A segment containing a sequence of words.
    :param n: The order of the n-grams.
    :param include_whitespace: If given, will not strip whitespaces from the line.
    :return: a dictionary containing ngrams and counts
    """
    if not include_whitespace:
        line = ''.join(line.split())

    return Counter([line[i:i + n] for i in range(len(line) - n + 1)])


def extract_all_char_ngrams(
        line: str, max_order: int, include_whitespace: bool = False) -> List[Counter]:
    """Extracts all character n-grams at once for convenience.

    :param line: A segment containing a sequence of words.
    :param max_order: The maximum order of the n-grams.
    :param include_whitespace: If given, will not strip whitespaces from the line.
    :return: a list of Counter objects containing ngrams and counts.
    """

    counters = []

    if not include_whitespace:
        line = ''.join(line.split())

    for n in range(1, max_order + 1):
        ngrams = Counter([line[i:i + n] for i in range(len(line) - n + 1)])
        counters.append(ngrams)

    return counters
