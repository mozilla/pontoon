
.. _poterminology_stopword_file:

Stopword file format
********************

.. versionadded:: 1.2

The default stopword file for :doc:`poterminology` describes the syntax of
these files and provides a good default for most applications using English
source text.  You can find the location of the default stopword file by looking
at the output of poterminology :opt:`--help`, or using the following command::

  poterminology --manpage | sed -n '/STOPFILE/s/.*(\(.*\)).*/\1/p'

.. _poterminology_stopword_file#overview:

Overview
========

The basic syntax of this file is line-oriented, with the first character of
each line determining its function.  The order of the lines is generally not
significant (with one exception noted below), and the selection of function
characters was made so that an ASCII sort of the file would leave it in a
generally logical order (except for comment lines).

Apart from comment lines (which begin with '#') and empty lines (which are also
ignored), there are three general types of lines, which may appear in any
order:

* case mapping specifiers
* stoplist regular expressions
* stoplist words

.. _poterminology_stopword_file#case_mapping_specifiers:

Case mapping specifiers
-----------------------

A line beginning with a '**!**' specifies upper-/lower-case mapping for words
or phrases before comparison with this stoplist (no mapping is applied to the
words or regular expressions in this file, only to the source messages).  The
second character on this line must be one of the following:

* **C** no uppercase / lowercase mapping is performed
* **F** 'Title Case" words / terms are folded to lower case (default)
* **I** all words are mapped to lowercase

These correspond to the equivalent :opt:`--preserve-case` /
:opt:`--fold-titlecase` / :opt:`--ignore-case` options to poterminology, but
are completely independent and only apply to stoplist matching.  You can run
poterminology with :opt:`-I` to map all terms to lowercase, and if the case
mapping specifier in the stopword file is '**!C**' a stoplist with "pootle" in
it will not prevent a term containing "Pootle" from passing the stoplist (and
then being mapped to "pootle").

There should only be one case mapping specifier in a stoplist file; if more
than one are present, the last one will take precedence over the others, and
its mapping will apply to all entries.  If multiple stoplist files are used,
the last case mapping specifier processed will apply to all entries **in all
files**.

.. _poterminology_stopword_file#stoplist_regular_expressions:

Stoplist regular expressions
----------------------------

Lines beginning with a '**/**' are regular expression patterns -- any word that
matches will be ignored by itself, and any phrase containing it will be
excluded as well.  The regular expression consists of all characters on the
line following the initial '/' -- these are extended regular expressions, so
grouping, alternation, and such are available.

Regular expression patterns are only checked if the word itself does not appear
in the stoplist file as a word entry.  The regular expression patterns are
always applied to individual words, not phrases, and must match the entire word
(i.e. they are anchored both at the start and end).

Use regular expressions sparingly, as evaluating them for every word in the
source files can be expensive.  In addition to stoplist regular expressions,
poterminology has precompiled patterns for C and Python format specifiers (e.g.
%d) and XML/HTML <elements> and &entities; -- these are removed before stoplist
processing and it is not possible to override this.

.. _poterminology_stopword_file#stoplist_words:

Stoplist words
--------------

All other lines should begin with one of the following characters, which
indicate whether the word should be **ignored** (as a word alone),
**disregarded** in a phrase (i.e. a phrase containing it is allowed, and the
word does not count against the :opt:`--term-words` length limit), or any
phrase containing it should be **excluded**.

* **+** allow word alone, allow phrases containing it
* **:** allow word alone, disregarded (for :opt:`--term-word-length`) inside
  phrase
* **<** allow word alone, but exclude any phrase containing it
* **=** ignore word alone, but allow phrases containing it
* **>** ignore word alone, disregarded (for :opt:`--term-word-length`) inside
  phrase
* **@** ignore word alone, and exclude any phrase containing it

Generally '+' is only needed for exceptions to regular expression patterns, but
it may also be used to override an entry in a previous stoplist if you are
using multiple stoplists.

Note that if a word appears multiple times in a stoplist file with different
function characters preceding it, the *last entry will take precedence* over
the others.  This is the only exception to the general rule that order is not
important in stopword files.

.. _poterminology_stopword_file#default_file_example:

Default file example
====================

::

  # apply title-case folding to words before comparing with this stoplist
  !F

The fold-titlecase setting is the default, even if it were not explicitly
specified.  This allows capitalized words at the start of a sentence (e.g.
"Who") to match a stopword "who" but allows acronyms like WHO (World Health
Organization) to be included in the terminology.  If you are using
poterminology with source files that contain large amounts of ALL UPPERCASE
TEXT you may find the ignore-case setting to be preferable.

::

  # override regex match below for phrases with 'no'
  +no

The regular expression /..? below would normally match the word 'no' and both
ignore it as a term and exclude any phrases containing it.  The above will
allow it to appear as a term and in phrases.

::

  # ignore all one or two-character words (unless =word appears below)
  /..?
  # ignore words with parenthesis, typically function() calls and the like
  /.*\(.*
  # ignore numbers, both cardinal (e.g. 1,234.0) and ordinal (e.g. 1st, 22nd)
  /[0-9,.]+(st|nd|rd|th)?

These regular expressions ignore a lot of uninteresting terms that are
typically code or other things that shouldn't be translated anyhow.  There are
many exceptions to the one or two-character word pattern in the default
stoplist file, not only with = like '=in' but also '+no' and ':on' and '<ok'
and '>of'.

::

  # allow these words by themselves and don't count against length for phrases
  :off
  :on

These prepositions are common as button text and thus useful to have as terms;
they also form an important part of phrases so are disregarded for term word
count to allow for slightly longer phrases including them.

::

  # allow these words by themselves, but ignore any phrases containing them
  <first
  <hello
  <last

These are words that are worth including in a terminology, as they are common
in applications, but which aren't generally part of idiomatic phrases.

::

  # ignore these words by themselves, but allow phrases containing them
  =able
  =about
  =actually
  =ad
  =as
  =at

This is the largest category of stoplist words, and these are all just rather
common words.  The purpose of a terminology list is to provide specific
translation suggestions for the harder words or phrases, not provide a general
dictionary, so these words are not of interest by themselves, but may well be
part of an interesting phrase.

::

  # ignore these words by themselves, but allow phrases containing them,   and
  # don't count against length for phrases
  #
  # (possible additions to this list for multi-lingual text: >di >el >le)
  #
  >a
  >an
  >and

These very common words aren't of interest by themselves, but often form an
important part of phrases so are disregarded for term word count to allow for
slightly longer phrases including them.

::

  # ignore these words and any phrases containing them
  @ain't
  @aint
  @al
  @are

These are "junk" words that are not only uninteresting by themselves, they
generally do not contribute anything to the phrases containing them.

