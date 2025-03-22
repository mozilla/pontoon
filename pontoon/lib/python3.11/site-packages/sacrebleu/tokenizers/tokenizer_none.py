from .tokenizer_base import BaseTokenizer

class NoneTokenizer(BaseTokenizer):
    """Don't apply any tokenization. Not recommended!."""

    def signature(self):
        return 'none'

    def __call__(self, line):
        return line
