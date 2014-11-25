
.. _pretranslate:

pretranslate
************

Merge existing translations from an old translation file to a new one as well
as fill any missing translations from translation memory via fuzzy matching.

This functionality used to be part of pot2po and corresponds to "msgmerge" from
the gettext package.

pretranslate works on PO and XLIFF files.

.. _pretranslate#usage:

Usage
=====

::

  pretranslate [options] <input> <output>

Where:

+-----------+------------------------------------------------------------+
| <input>   | is the translation file or directory to be pretranslated   |
+-----------+------------------------------------------------------------+
| <output>  | is the translation file or a directory where the           |
|           | pretranslated version will be stored                       |
+-----------+------------------------------------------------------------+

Options:

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-iINPUT, --input=INPUT   read from INPUT in pot format
-xEXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-oOUTPUT, --output=OUTPUT     write to OUTPUT in po, pot formats
-tTEMPLATE, --template=TEMPLATE   read old translations from TEMPLATE
--tm=TM              The file to use as translation memory when fuzzy matching
-sMIN_SIMILARITY, --similarity=MIN_SIMILARITY   The minimum similarity for inclusion (default: 75%)
--nofuzzymatching    Disable all fuzzy matching

.. _pretranslate#examples:

Examples
========

::

  pretranslate -t zu-1.0.1 -tm zu_tm.po zu-2.0.2 zu-2.0.2-translated

Here we are pretranslating the PO or XLIFF files in *zu-2.0.2* using the old
translations in *zu-1.0.1* and fuzzy matches from the zu_tm.po compendium. the
result is stored in *zu-2.0.2-translate*

Unlike pot2po pretranslate will not change anything in the input file except
merge translations, no reordering or changes to headers.

.. _pretranslate#merging:

Merging
=======

It helps to understand when and how pretranslate will merge. The default is to
follow msgmerge's behaviour but we add some extra features with fuzzy matching:

* If everything matches we carry that across
* We can resurrect obsolete messages for reuse
* If we cannot find a match we will first look through the current and obsolete
  messages and then through any global translation memory
* Fuzzy matching makes use of the :doc:`Levenshtein distance
  <levenshtein_distance>` algorithm to detect the best matches

.. _pretranslate#performance:

Performance
===========

Fuzzy matches are usually of good quality. Installation of the
`python-Levenshtein
<https://pypi.python.org/pypi/python-Levenshtein>`_
package will speed up fuzzy matching. Without this a Python based matcher is
used which is considerably slower.
