# -*- coding: utf-8 -*-

from __future__ import print_function

import re
from collections import defaultdict, Counter
from functools import partial
from itertools import chain

from sacremoses.corpus import Perluniprops
from sacremoses.util import parallelize_preprocess, grouper


perluniprops = Perluniprops()


class MosesTruecaser(object):
    """
    This is a Python port of the Moses Truecaser from
    https://github.com/moses-smt/mosesdecoder/blob/master/scripts/recaser/train-truecaser.perl
    https://github.com/moses-smt/mosesdecoder/blob/master/scripts/recaser/truecase.perl
    """

    # Perl Unicode Properties character sets.
    Lowercase_Letter = str("".join(perluniprops.chars("Lowercase_Letter")))
    Uppercase_Letter = str("".join(perluniprops.chars("Uppercase_Letter")))
    Titlecase_Letter = str("".join(perluniprops.chars("Uppercase_Letter")))

    def __init__(self, load_from=None, is_asr=None, encoding="utf8"):
        """
        :param load_from:
        :type load_from:

        :param is_asr: A flag to indicate that model is for ASR. ASR input has
            no case, make sure it is lowercase, and make sure known are cased
            eg. 'i' to be uppercased even if i is known.
        :type is_asr: bool
        """
        # Initialize the object.
        super(MosesTruecaser, self).__init__()
        # Initialize the language specific nonbreaking prefixes.
        self.SKIP_LETTERS_REGEX = re.compile(
            "[{}{}{}]".format(
                self.Lowercase_Letter, self.Uppercase_Letter, self.Titlecase_Letter
            )
        )

        self.XML_SPLIT_REGX = re.compile("(<.*(?<=>))(.*)((?=</)[^>]*>)")

        self.SENT_END = {".", ":", "?", "!"}
        self.DELAYED_SENT_START = {
            "(",
            "[",
            '"',
            "'",
            "&apos;",
            "&quot;",
            "&#91;",
            "&#93;",
        }

        self.encoding = encoding

        self.is_asr = is_asr
        if load_from:
            self.model = self._load_model(load_from)

    def learn_truecase_weights(self, tokens, possibly_use_first_token=False):
        """
        This function checks through each tokens in a sentence and returns the
        appropriate weight of each surface token form.
        """
        # Keep track of first tokens in the sentence(s) of the line.
        is_first_word = True
        truecase_weights = []
        for i, token in enumerate(tokens):
            # Skip XML tags.
            if re.search(r"(<\S[^>]*>)", token):
                continue
            # Skip if sentence start symbols.
            elif token in self.DELAYED_SENT_START:
                continue

            # Resets the `is_first_word` after seeing sent end symbols.
            if not is_first_word and token in self.SENT_END:
                is_first_word = True
                continue
            # Skips tokens with nothing to case.
            if not self.SKIP_LETTERS_REGEX.search(token):
                is_first_word = False
                continue

            # If it's not the first word,
            # then set the current word weight to 1.
            current_word_weight = 0
            if not is_first_word:
                current_word_weight = 1
            # Otherwise check whether user wants to optionally
            # use the first word.
            elif possibly_use_first_token:
                # Gated special handling of first word of sentence.
                # Check if first characer of token is lowercase.
                if token[0].islower():
                    current_word_weight = 1
                elif i == 1:
                    current_word_weight = 0.1

            is_first_word = False

            if current_word_weight > 0:
                truecase_weights.append((token.lower(), token, current_word_weight))
        return truecase_weights

    def _train(
        self,
        document_iterator,
        save_to=None,
        possibly_use_first_token=False,
        processes=1,
        progress_bar=False,
    ):
        """
        :param document_iterator: The input document, each outer list is a sentence,
                          the inner list is the list of tokens for each sentence.
        :type document_iterator: iter(list(str))

        :param possibly_use_first_token: When True, on the basis that the first
            word of a sentence is always capitalized; if this option is provided then:
            a) if a sentence-initial token is *not* capitalized, then it is counted, and
            b) if a capitalized sentence-initial token is the only token of the segment,
               then it is counted, but with only 10% of the weight of a normal token.
        :type possibly_use_first_token: bool

        :returns: A dictionary of the best, known objects as values from `_casing_to_model()`
        :rtype: {'best': dict, 'known': Counter}
        """
        casing = defaultdict(Counter)
        train_truecaser = partial(
            self.learn_truecase_weights,
            possibly_use_first_token=possibly_use_first_token,
        )
        token_weights = chain(
            *parallelize_preprocess(
                train_truecaser, document_iterator, processes, progress_bar=progress_bar
            )
        )
        # Collect the token_weights from every sentence.
        for lowercase_token, surface_token, weight in token_weights:
            casing[lowercase_token][surface_token] += weight

        # Save to file if specified.
        if save_to:
            self._save_model_from_casing(casing, save_to)
        return self._casing_to_model(casing)

    def train(
        self,
        documents,
        save_to=None,
        possibly_use_first_token=False,
        processes=1,
        progress_bar=False,
    ):
        """
        Default duck-type of _train(), accepts list(list(str)) as input documents.
        """
        self.model = None  # Clear the model first.
        self.model = self._train(
            documents,
            save_to,
            possibly_use_first_token,
            processes,
            progress_bar=progress_bar,
        )
        return self.model

    def train_from_file(
        self,
        filename,
        save_to=None,
        possibly_use_first_token=False,
        processes=1,
        progress_bar=False,
    ):
        """
        Duck-type of _train(), accepts a filename to read as a `iter(list(str))`
        object.
        """
        with open(filename, encoding=self.encoding) as fin:
            # document_iterator = map(str.split, fin.readlines())
            document_iterator = (
                line.split() for line in fin.readlines()
            )  # Lets try a generator comprehension for Python2...
        self.model = None  # Clear the model first.
        self.model = self._train(
            document_iterator,
            save_to,
            possibly_use_first_token,
            processes,
            progress_bar=progress_bar,
        )
        return self.model

    def train_from_file_object(
        self,
        file_object,
        save_to=None,
        possibly_use_first_token=False,
        processes=1,
        progress_bar=False,
    ):
        """
        Duck-type of _train(), accepts a file object to read as a `iter(list(str))`
        object.
        """
        # document_iterator = map(str.split, file_object.readlines())
        document_iterator = (
            line.split() for line in file_object.readlines()
        )  # Lets try a generator comprehension for Python2...
        self.model = None  # Clear the model first.
        self.model = self._train(
            document_iterator,
            save_to,
            possibly_use_first_token,
            processes,
            progress_bar=progress_bar,
        )
        return self.model

    def truecase(self, text, return_str=False, use_known=False):
        """
        Truecase a single sentence / line of text.

        :param text: A single string, i.e. sentence text.
        :type text: str

        :param use_known: Use the known case if a word is a known word but not the first word.
        :type use_known: bool
        """
        check_model_message = str(
            "\nUse Truecaser.train() to train a model.\n"
            "Or use Truecaser('modefile') to load a model."
        )
        assert hasattr(self, "model"), check_model_message
        # Keep track of first tokens in the sentence(s) of the line.
        is_first_word = True
        truecased_tokens = []
        tokens = self.split_xml(text)
        # best_cases = best_cases if best_cases else self.model['best']
        # known_cases = known_cases if known_cases else self.model['known']

        for i, token in enumerate(tokens):

            # Append XML tags and continue
            if re.search(r"(<\S[^>]*>)", token):
                truecased_tokens.append(token)
                continue

            # Note this shouldn't happen other if | are escaped as &#124;
            # To make the truecaser resilient,
            # we'll just any token starting with pipes as they are.
            if token == "|" or token.startswith("|"):
                truecased_tokens.append(token)
                continue

            # Reads the word token and factors separatedly
            token, other_factors = re.search(r"^([^\|]+)(.*)", token).groups()

            # Lowercase the ASR tokens.
            if self.is_asr:
                token = token.lower()

            # The actual case replacement happens here.
            # "Most frequent" case of the word.
            best_case = self.model["best"].get(token.lower(), None)
            # If it's the start of sentence.
            if is_first_word and best_case:  # Truecase sentence start.
                token = best_case
            elif use_known and token in self.model["known"]:  # Don't change known tokens.
                pass
            elif best_case:  # Truecase otherwise unknown tokens? Heh? From https://github.com/moses-smt/mosesdecoder/blob/master/scripts/recaser/truecase.perl#L66
                token = best_case
            # Else, it's an unknown word, don't change the word.
            # Concat the truecased `word` with the `other_factors`
            token = token + other_factors
            # Adds the truecased word.
            truecased_tokens.append(token)

            # Resets sentence start if this token is an ending punctuation.
            if token in self.SENT_END:
                is_first_word = True
            elif token not in self.DELAYED_SENT_START:
                is_first_word = False

        # return ' '.join(tokens)
        return " ".join(truecased_tokens) if return_str else truecased_tokens

    def truecase_file(self, filename, return_str=True):
        with open(filename, encoding=self.encoding) as fin:
            for line in fin:
                truecased_tokens = self.truecase(line.strip())
                # Yield the truecased line.
                yield " ".join(truecased_tokens) if return_str else truecased_tokens

    @staticmethod
    def split_xml(line):
        """
        Python port of split_xml function in Moses' truecaser:
        https://github.com/moses-smt/mosesdecoder/blob/master/scripts/recaser/truecaser.perl

        :param line: Input string, should be tokenized, separated by space.
        :type line: str
        """
        line = line.strip()
        tokens = []
        while line:
            # Assumes that xml tag is always separated by space.
            has_xml = re.search(r"^\s*(<\S[^>]*>)(.*)$", line)
            # non-XML test.
            is_non_xml = re.search(r"^\s*([^\s<>]+)(.*)$", line)
            # '<' or '>' occurs in word, but it's not an XML tag
            xml_cognates = re.search(r"^\s*(\S+)(.*)$", line)
            if has_xml:
                potential_xml, line_next = has_xml.groups()
                # exception for factor that is an XML tag
                if (
                    re.search(r"^\S", line)
                    and len(tokens) > 0
                    and re.search(r"\|$", tokens[-1])
                ):
                    tokens[-1] += potential_xml
                    # If it's a token with factors, join with the previous token.
                    is_factor = re.search(r"^(\|+)(.*)$", line_next)
                    if is_factor:
                        tokens[-1] += is_factor.group(1)
                        line_next = is_factor.group(2)
                else:
                    tokens.append(
                        potential_xml + " "
                    )  # Token hack, unique to sacremoses.
                line = line_next

            elif is_non_xml:
                tokens.append(is_non_xml.group(1))  # Token hack, unique to sacremoses.
                line = is_non_xml.group(2)
            elif xml_cognates:
                tokens.append(
                    xml_cognates.group(1)
                )  # Token hack, unique to sacremoses.
                line = xml_cognates.group(2)
            else:
                raise Exception("ERROR: huh? {}".format(line))
            tokens[-1] = tokens[-1].strip()  # Token hack, unique to sacremoses.
        return tokens

    def _casing_to_model(self, casing):
        """

        :returns: A tuple of the (best, known) objects.
        :rtype: tuple(dict, Counter)
        """
        best = {}
        known = Counter()

        for token_lower in casing:
            tokens = casing[token_lower].most_common()
            # Set the most frequent case as the "best" case.
            best[token_lower] = tokens[0][0]
            # If it's asr, throw away everything
            if not self.is_asr:
                for token, count in tokens[1:]:
                    # Note: This is rather odd that the counts are thrown away...
                    # from https://github.com/moses-smt/mosesdecoder/blob/master/scripts/recaser/truecase.perl#L34
                    known[token] += 1
        model = {"best": best, "known": known, "casing": casing}
        return model

    def save_model(self, filename):
        self._save_model_from_casing(self.model["casing"], filename)

    def _save_model_from_casing(self, casing, filename):
        """
        Outputs the truecaser model file in the same output format as
        https://github.com/moses-smt/mosesdecoder/blob/master/scripts/recaser/train-truecaser.perl

        :param casing: The dictionary of tokens counter from `train()`.
        :type casing: default(Counter)
        """
        with open(filename, "w", encoding=self.encoding) as fout:
            for token in casing:
                total_token_count = sum(casing[token].values())
                tokens_counts = []
                for i, (token, count) in enumerate(casing[token].most_common()):
                    if i == 0:
                        out_token = "{} ({}/{})".format(token, count, total_token_count)
                    else:
                        out_token = "{} ({})".format(token, count, total_token_count)
                    tokens_counts.append(out_token)
                print(" ".join(tokens_counts), end="\n", file=fout)

    def _load_model(self, filename):
        """
        Loads pre-trained truecasing file.

        :returns: A dictionary of the best, known objects as values from `_casing_to_model()`
        :rtype: {'best': dict, 'known': Counter}
        """
        casing = defaultdict(Counter)
        with open(filename, encoding=self.encoding) as fin:
            for line in fin:
                line = line.strip().split()
                for token, count in grouper(line, 2):
                    count = count.split("/")[0].strip("()")
                    casing[token.lower()][token] = int(count)
        # Returns the best and known object from `_casing_to_model()`
        return self._casing_to_model(casing)


class MosesDetruecaser(object):
    def __init__(self):
        # Initialize the object.
        super(MosesDetruecaser, self).__init__()
        self.SENT_END = {".", ":", "?", "!"}
        self.DELAYED_SENT_START = {
            "(",
            "[",
            '"',
            "'",
            "&apos;",
            "&quot;",
            "&#91;",
            "&#93;",
        }

        # Some predefined tokens that will always be in lowercase.
        self.ALWAYS_LOWER = {
            "a",
            "after",
            "against",
            "al-.+",
            "and",
            "any",
            "as",
            "at",
            "be",
            "because",
            "between",
            "by",
            "during",
            "el-.+",
            "for",
            "from",
            "his",
            "in",
            "is",
            "its",
            "last",
            "not",
            "of",
            "off",
            "on",
            "than",
            "the",
            "their",
            "this",
            "to",
            "was",
            "were",
            "which",
            "will",
            "with",
        }

    def detruecase(self, text, is_headline=False, return_str=False):
        """
        Detruecase the translated files from a model that learnt from truecased
        tokens.

        :param text: A single string, i.e. sentence text.
        :type text: str
        """
        # `cased_tokens` keep tracks of detruecased tokens.
        cased_tokens = []
        sentence_start = True
        # Capitalize token if it's at the sentence start.
        for token in text.split():
            token = token[:1].upper() + token[1:] if sentence_start else token
            cased_tokens.append(token)
            if token in self.SENT_END:
                sentence_start = True
            elif not token in self.DELAYED_SENT_START:
                sentence_start = False
        # Check if it's a headline, if so then use title case.
        if is_headline:
            cased_tokens = [
                token if token in self.ALWAYS_LOWER else token[:1].upper() + token[1:]
                for token in cased_tokens
            ]

        return " ".join(cased_tokens) if return_str else cased_tokens


__all__ = ["MosesTruecaser", "MosesDetruecaser"]
