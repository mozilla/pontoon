from typing import Sequence, Optional

from .metrics import BLEU, CHRF, TER, BLEUScore, CHRFScore, TERScore


######################################################################
# Backward compatibility functions for old style API access (< 1.4.11)
######################################################################
def corpus_bleu(hypotheses: Sequence[str],
                references: Sequence[Sequence[str]],
                smooth_method='exp',
                smooth_value=None,
                force=False,
                lowercase=False,
                tokenize=BLEU.TOKENIZER_DEFAULT,
                use_effective_order=False) -> BLEUScore:
    """Computes BLEU for a corpus against a single (or multiple) reference(s).
    This is the main CLI entry point for computing BLEU between a system output
    and a reference sentence.

    :param hypotheses: A sequence of hypothesis strings.
    :param references: A sequence of reference documents with document being
        defined as a sequence of reference strings.
    :param smooth_method: The smoothing method to use ('floor', 'add-k', 'exp' or 'none')
    :param smooth_value: The smoothing value for `floor` and `add-k` methods. `None` falls back to default value.
    :param force: Ignore data that looks already tokenized
    :param lowercase: Lowercase the data
    :param tokenize: The tokenizer to use
    :param use_effective_order: Don't take into account n-gram orders without any match.
    :return: a `BLEUScore` object
    """
    metric = BLEU(
        lowercase=lowercase, force=force, tokenize=tokenize,
        smooth_method=smooth_method, smooth_value=smooth_value,
        effective_order=use_effective_order)

    return metric.corpus_score(hypotheses, references)


def raw_corpus_bleu(hypotheses: Sequence[str],
                    references: Sequence[Sequence[str]],
                    smooth_value: Optional[float] = BLEU.SMOOTH_DEFAULTS['floor']) -> BLEUScore:
    """Computes BLEU for a corpus against a single (or multiple) reference(s).
    This convenience function assumes a particular set of arguments i.e.
    it disables tokenization and applies a `floor` smoothing with value `0.1`.

    This convenience call does not apply any tokenization at all,
    neither to the system output nor the reference. It just computes
    BLEU on the "raw corpus" (hence the name).

    :param hypotheses: A sequence of hypothesis strings.
    :param references: A sequence of reference documents with document being
        defined as a sequence of reference strings.
    :param smooth_value: The smoothing value for `floor`. If not given, the default of 0.1 is used.
    :return: Returns a `BLEUScore` object.

    """
    return corpus_bleu(
        hypotheses, references, smooth_method='floor',
        smooth_value=smooth_value, force=True, tokenize='none',
        use_effective_order=True)


def sentence_bleu(hypothesis: str,
                  references: Sequence[str],
                  smooth_method: str = 'exp',
                  smooth_value: Optional[float] = None,
                  lowercase: bool = False,
                  tokenize=BLEU.TOKENIZER_DEFAULT,
                  use_effective_order: bool = True) -> BLEUScore:
    """
    Computes BLEU for a single sentence against a single (or multiple) reference(s).

    Disclaimer: Computing BLEU at the sentence level is not its intended use as
    BLEU is a corpus-level metric.

    :param hypothesis: A single hypothesis string.
    :param references: A sequence of reference strings.
    :param smooth_method: The smoothing method to use ('floor', 'add-k', 'exp' or 'none')
    :param smooth_value: The smoothing value for `floor` and `add-k` methods. `None` falls back to default value.
    :param lowercase: Lowercase the data
    :param tokenize: The tokenizer to use
    :param use_effective_order: Don't take into account n-gram orders without any match.
    :return: Returns a `BLEUScore` object.
    """
    metric = BLEU(
        lowercase=lowercase, tokenize=tokenize, force=False,
        smooth_method=smooth_method, smooth_value=smooth_value,
        effective_order=use_effective_order)

    return metric.sentence_score(hypothesis, references)


def corpus_chrf(hypotheses: Sequence[str],
                references: Sequence[Sequence[str]],
                char_order: int = CHRF.CHAR_ORDER,
                word_order: int = CHRF.WORD_ORDER,
                beta: int = CHRF.BETA,
                remove_whitespace: bool = True,
                eps_smoothing: bool = False) -> CHRFScore:
    """
    Computes chrF for a corpus against a single (or multiple) reference(s).
    If `word_order` equals to 2, the metric is referred to as chrF++.

    :param hypotheses: A sequence of hypothesis strings.
    :param references: A sequence of reference documents with document being
        defined as a sequence of reference strings.
    :param char_order: Character n-gram order.
    :param word_order: Word n-gram order. If equals to 2, the metric is referred to as chrF++.
    :param beta: Determine the importance of recall w.r.t precision.
    :param eps_smoothing: If `True`, applies epsilon smoothing similar
    to reference chrF++.py, NLTK and Moses implementations. Otherwise,
    it takes into account effective match order similar to sacreBLEU < 2.0.0.
    :param remove_whitespace: If `True`, removes whitespaces prior to character n-gram extraction.
    :return: A `CHRFScore` object.
    """
    metric = CHRF(
        char_order=char_order,
        word_order=word_order,
        beta=beta,
        whitespace=not remove_whitespace,
        eps_smoothing=eps_smoothing)
    return metric.corpus_score(hypotheses, references)


def sentence_chrf(hypothesis: str,
                  references: Sequence[str],
                  char_order: int = CHRF.CHAR_ORDER,
                  word_order: int = CHRF.WORD_ORDER,
                  beta: int = CHRF.BETA,
                  remove_whitespace: bool = True,
                  eps_smoothing: bool = False) -> CHRFScore:
    """
    Computes chrF for a single sentence against a single (or multiple) reference(s).
    If `word_order` equals to 2, the metric is referred to as chrF++.

    :param hypothesis: A single hypothesis string.
    :param references: A sequence of reference strings.
    :param char_order: Character n-gram order.
    :param word_order: Word n-gram order. If equals to 2, the metric is referred to as chrF++.
    :param beta: Determine the importance of recall w.r.t precision.
    :param eps_smoothing: If `True`, applies epsilon smoothing similar
    to reference chrF++.py, NLTK and Moses implementations. Otherwise,
    it takes into account effective match order similar to sacreBLEU < 2.0.0.
    :param remove_whitespace: If `True`, removes whitespaces prior to character n-gram extraction.
    :return: A `CHRFScore` object.
    """
    metric = CHRF(
        char_order=char_order,
        word_order=word_order,
        beta=beta,
        whitespace=not remove_whitespace,
        eps_smoothing=eps_smoothing)
    return metric.sentence_score(hypothesis, references)


def corpus_ter(hypotheses: Sequence[str],
               references: Sequence[Sequence[str]],
               normalized: bool = False,
               no_punct: bool = False,
               asian_support: bool = False,
               case_sensitive: bool = False) -> TERScore:
    """
    Computes TER for a corpus against a single (or multiple) reference(s).

    :param hypotheses: A sequence of hypothesis strings.
    :param references: A sequence of reference documents with document being
        defined as a sequence of reference strings.
    :param normalized: Enable character normalization.
    :param no_punct: Remove punctuation.
    :param asian_support: Enable special treatment of Asian characters.
    :param case_sensitive: Enables case-sensitivity.
    :return: A `TERScore` object.
    """
    metric = TER(
        normalized=normalized,
        no_punct=no_punct,
        asian_support=asian_support,
        case_sensitive=case_sensitive)
    return metric.corpus_score(hypotheses, references)


def sentence_ter(hypothesis: str,
                 references: Sequence[str],
                 normalized: bool = False,
                 no_punct: bool = False,
                 asian_support: bool = False,
                 case_sensitive: bool = False) -> TERScore:
    """
    Computes TER for a single hypothesis against a single (or multiple) reference(s).

    :param hypothesis: A single hypothesis string.
    :param references: A sequence of reference strings.
    :param normalized: Enable character normalization.
    :param no_punct: Remove punctuation.
    :param asian_support: Enable special treatment of Asian characters.
    :param case_sensitive: Enable case-sensitivity.
    :return: A `TERScore` object.
    """
    metric = TER(
        normalized=normalized,
        no_punct=no_punct,
        asian_support=asian_support,
        case_sensitive=case_sensitive)
    return metric.sentence_score(hypothesis, references)
