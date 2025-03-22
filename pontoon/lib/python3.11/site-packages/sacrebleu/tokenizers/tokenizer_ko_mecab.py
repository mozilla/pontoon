from functools import lru_cache

try:
    import mecab_ko as MeCab
    import mecab_ko_dic
except ImportError:
    # Don't fail until the tokenizer is actually used
    MeCab = None

from .tokenizer_base import BaseTokenizer

FAIL_MESSAGE = """
Korean tokenization requires extra dependencies, but you do not have them installed.
Please install them like so.

    pip install sacrebleu[ko]
"""


class TokenizerKoMecab(BaseTokenizer):
    def __init__(self):
        if MeCab is None:
            raise RuntimeError(FAIL_MESSAGE)
        self.tagger = MeCab.Tagger(mecab_ko_dic.MECAB_ARGS + " -Owakati")

        # make sure the dictionary is mecab-ko-dic
        d = self.tagger.dictionary_info()
        assert d.size == 811795, \
            "Please make sure to use the mecab-ko-dic for MeCab-ko"
        # This asserts that no user dictionary has been loaded
        assert d.next is None

    @lru_cache(maxsize=2**16)
    def __call__(self, line):
        """
        Tokenizes an Korean input line using MeCab-ko morphological analyzer.

        :param line: a segment to tokenize
        :return: the tokenized line
        """
        line = line.strip()
        sentence = self.tagger.parse(line).strip()
        return sentence

    def signature(self):
        """
        Returns the MeCab-ko parameters.

        :return: signature string
        """
        signature = self.tagger.version() + "-KO"
        return 'ko-mecab-' + signature
