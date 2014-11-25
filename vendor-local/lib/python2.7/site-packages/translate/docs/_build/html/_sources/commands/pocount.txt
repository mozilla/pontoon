
.. _pocount:

pocount
*******

pocount will count the number of strings and words in translatable files.

Supported formates include: PO and XLIFF.   Almost all bilingual file formats
supported by the Translate Toolkit will work with pocount, including: :doc:`TMX
</formats/tmx>`, :doc:`TBX </formats/tbx>`, :doc:`Gettext .mo </formats/mo>`,
:doc:`Qt .qm </formats/qm>`, :doc:`Wordfast .txt TM </formats/wordfast>`.

A number of other :doc:`formats </formats/index>` should be countable as the
toolkit develops.  Note that only multilingual formats based the storage
:doc:`base class </formats/base_classes>` are supported, but that includes
almost all storage formats.

.. _pocount#usage:

Usage
=====

::

  pocount [options] <directory|file(s)>

Where:

+------------+--------------------------------------------------------------+
| directory  | will recurse and count all files in the specified directory  |
+------------+--------------------------------------------------------------+
| file(s)    | will count all files specified                               |
+------------+--------------------------------------------------------------+

Options:

-h, --help       show this help message and exit
--incomplete     skip 100% translated files

Output format:

--full           (default) statistics in full, verbose format
--csv            statistics in CSV format
--short          same as --short-strings
--short-strings  statistics of strings in short format -- one line per file
--short-words    statistics of words in short format -- one line per file

.. _pocount#examples:

Examples
========

pocount makes it easy to count the current state of a body of translations. The
most interesting options are those that adjust the output style and decide what
to count.

.. _pocount#easy_counting:

Easy counting
-------------

To count how much work is to be done in you project::

  pocount project/

This will count all translatable files found in the directory *project*/ and
output the results in :opt:`--full` format.

You might want to be more specific and only count certain files::

  pocount *.po

This will count all PO files in the current directory but will ignore any other
files that 'pocount' can count.

You can have full control of the files to count by using some of the abilities
of the Unix commandline, these may work on Mac OS X but are unlikely to work on
Windows.::

  pocount $(find . -name "*.properties.po")

This will first find all files that match ``*.properties.po`` and then count
them.  That would make it easy to count the state of your Mozilla translations
of .properties files.

.. _pocount#incomplete_work:

Incomplete work
---------------

To count what still needs to be done, ignoring what is 100% complete you can
use the :opt:`--incomplete` option.::

  pocount --incomplete --short *.xlf

We are now counting all XLIFF files by using the ``*.xlf`` expansion.  We are
only counting files that are not 100% complete and we're outputing string
counts using the :opt:`--short` option.

.. _pocount#output_formats:

Output formats
==============

The output options provide the following types of output

.. _pocount#--full:

--full
------

This is the normal, or default, mode.  It produces the most comprehensive and
easy to read data, although the amount of data may overwhelm the user. It
produces the following output::

  avmedia/source/viewer.po
  type              strings      words (source)    words (translation)
  translated:   73465 ( 99%)     538598 ( 99%)          513296
  fuzzy:           13 (  0%)        141 (  0%)             n/a
  untranslated:    53 (  0%)        602 (  0%)             n/a
  Total:        73531            539341                 513296

A grand total and file count is provided if the number of files is greater than
one.

.. _pocount#--csv:

--csv
-----

This format is useful if you want to reuse the data in a spreadsheet.  In CSV
mode the following output is shown::

  Filename, Translated Messages, Translated Source Words, Translated Target Words, Fuzzy Messages, Fuzzy Source Words, Untranslated Messages, Untranslated Source Words, Review Messages, Review Source Words
  avmedia/source/viewer.po,  1, 3, 3, 0, 0, 4, 22, 1, 3

Totals are not provided in CSV mode.

.. _pocount#--short-strings_alias_--short:

--short-strings (alias --short)
-------------------------------

The focus is on easily accessible data in a compact form.  This will only count
strings and uses a short syntax to make it easy for an experienced localiser to
read.::

  test-po/fuzzy.po strings: total: 1	| 0t	1f	0u	| 0%t	100%f	0%u

The filename is followed by a word indicating the type of count, here we are
counting strings.  The total give the total string count.  While the letters t,
f and u represent 'translated', 'fuzzy' and 'untranslated' and here indicate
the string counts for each of those categories.  The counts are followed by a
percentage representation of the same categories.

.. _pocount#--short-words:

--short-words
-------------

The output is very similar to :opt:`--short-strings` above::

  test-po/fuzzy.po source words: total: 3	| 0t	3f	0u	| 0%t	100%f	0%u

But instead of counting string we are now counting words as indicated by the
term 'source words'

.. _pocount#bugs:

Bugs
====

* There are some miscounts related to word breaks.
* When using the short output formats the columns may not be exactly aligned.
  This is because the number of digits in different columns is unknown before
  all input files are processed. The chosen tradeoff here was instanteous
  output (after each processed file) instead of waiting for the last file to be
  processed.

