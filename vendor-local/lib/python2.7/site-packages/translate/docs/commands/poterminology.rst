
.. _poterminology:

poterminology
*************

poterminology takes Gettext PO/POT files and extracts potential terminology.

This is useful as a first step before translating a new project (or an existing
project into a new target language) as it allows you to define key terminology
for consistency in translations.  The resulting terminology PO files can be
used by Pootle to provide suggestions while translating.

Generally, all the input files should have the same source language, and either
be POT files (with no translations) or PO files with translations to the same
target language.

The more separate PO files you use to generate terminology, the better your
results will be, but poterminology can be used with just a single input file.

Read more about :wp:`terminology extraction <Terminology_extraction>`

.. _poterminology#usage:

Usage
=====

::

  poterminology [options] <input> <terminology>

Where:

+-----------------+-----------------------------------------------+
| <input>         | translations to be examined for terminology   |
+-----------------+-----------------------------------------------+
| <terminology>   | extracted potential terminology               |
+-----------------+-----------------------------------------------+

Options:

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT   read from INPUT in pot, po formats
-x EXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT     write to OUTPUT in po, pot formats
-u UPDATEFILE, --update=UPDATEFILE  update terminology in UPDATEFILE
-S STOPFILE, --stopword-list=STOPFILE  read stopword (term exclusion) list from STOPFILE (default site-packages/translate/share/stoplist-en)
-F, --fold-titlecase  fold "Title Case" to lowercase (default)
-C, --preserve-case   preserve all uppercase/lowercase
-I, --ignore-case     make all terms lowercase
--accelerator=ACCELERATORS  ignore the given accelerator characters when matching (accelerator characters probably require quoting)
-t LENGTH, --term-words=LENGTH  generate terms of up to LENGTH words (default 3)
--inputs-needed=MIN   omit terms appearing in less than MIN input files (default 2, or 1 if only one input file)
--fullmsg-needed=MIN  omit full message terms appearing in less than MIN different messages (default 1)
--substr-needed=MIN   omit substring-only terms appearing in less than MIN different messages (default 2)
--locs-needed=MIN     omit terms appearing in less than MIN different original program locations (default 2)
--sort=ORDER          output sort order(s): frequency, dictionary, length (default is all orders in the above priority)
--source-language=LANG  the source language code (default 'en')
-v, --invert          invert the source and target languages for terminology

.. _poterminology#examples:

Examples
========

You want to generate a terminology file for Pootle that will be used to provide
suggestions for translating Pootle itself::

  poterminology Pootle/po/pootle/templates/*.pot .

This results in a ``./pootle-terminology.pot`` output file with 23 terms (from
"file" to "does not exist") -- without any translations.

The default output file can be added to a Pootle project to provide
:ref:`terminology matching <pootle:terminology>` suggestions for that project;
alternately a special Terminology project can be used and it will provide
terminology suggestions for all projects that do not have a
pootle-terminology.po file.

Generating a terminology file containing automatically extracted translations
is possible as well, by using PO files with translations for the input files::

  poterminology Pootle/po/pootle/fi/*.po --output fi/pootle-terminology.po --sort dictionary

Using PO files with Finnish translations, you get an output file that contains
the same 23 terms, with translations of eight terms -- one ("login") is fuzzy
due to slightly different translations in jToolkit and Pootle.  The file is
sorted in alphabetical order (by source term, not translated term), which can
be useful when comparing different terminology files.

Even though there is no translation of Pootle into Kinyarwanda, you can use the
Gnome UI terminology PO file as a source for translations; in order to extract
only the terms common to jToolkit and Pootle this command includes the POT
output from the first step above (which is redundant) and require terms to
appear in three different input sources::

  poterminology Pootle/po/pootle/templates/*.pot pootle-terminology.pot \
    Pootle/po/terminology/rw/gnome/rw.po --inputs-needed=3 -o terminology/rw.po

Of the 23 terms, 16 have Kinyarwanda translations extracted from the Gnome UI
terminology.

For a language like Spanish, with both Pootle translations and Gnome
terminology available, 18 translations (2 fuzzy) are generated by the following
command, which initializes the terminology file from the POT output from the
first step, and then uses :opt:`--update` to specify that the pootle-es.po file
is to be used both for input and output::

  cp pootle-terminology.pot glossary-es.po
  poterminology --inputs=3 --update glossary-es.po \
    Pootle/po/pootle/es/*.po Pootle/po/terminology/es/gnome/es.po

.. _poterminology#reduced_terminology_glossaries:

Reduced terminology glossaries
------------------------------

If you want to generate a terminology file containing only single words,  not
phrases, you can use :opt:`-t`/:opt:`--term-words` to control this.  If your
input files are very large and/or you have a lot of input files, and you are
finding that poterminology is taking too much time and memory to run, reducing
the phrase size from the default value of 3 can be helpful.

For example, running poterminology on the subversion trunk with the default
phrase size can take quite some time and may not even complete on a
small-memory system, but with :opt:`--term-words=1` the initial number of terms
is reduced by half, and the thresholding process can complete::

  poterminology --progress=none -t 1 translate

  1297 terms from 64039 units in 216 files
  254 terms after thresholding
  254 terms after subphrase reduction

The first line of output indicates the number of input files and translation
units (messages), with the number of unique terms present after removing C and
Python format specifiers (e.g. %d), XML/HTML <elements> and &entities; and
performing stoplist elimination.

The second line gives the number of terms remaining after applying threshold
filtering (discussed in more detail below) to eliminate terms that are not
sufficiently "common" in the input files.

The third line gives the number of terms remaining after eliminating subphrases
that did not occur independently.  In this case, since the term-words limit is
1, there are no subphrases and so the number is the same as on the second line.

However, in the first example above (generating terminology for Pootle itself),
the term "not exist" passes the stoplist and threshold filters, but all
occurrences of this term also contained the term "does not exist" which also
passes the stoplist and threshold filters.  Given this duplication, the shorter
phrase is eliminated in favor of the longer one, resulting in 23 terms (out of
25 that pass the threshold filters).

.. _poterminology#reducing_output_terminology_with_thresholding_options:

Reducing output terminology with thresholding options
=====================================================

Depending on the size and number of the source files, and the desired scope of
the output terminology file, there are several thresholding filters that can be
adjusted to allow fewer or more terms in the output file.  We have seen above
how one (:opt:`--inputs-needed`) can be used to require that terms be present
in multiple input files, but there are also other thresholds that can be
adjusted to control the size of the output terminology file.

--inputs-needed
---------------

This is the most flexible and powerful thresholding control.  The default value
is 2, unless only one input file (not counting an :opt:`--update argument`) is
provided, in which case the threshold is 1 to avoid filtering out all terms and
generating an empty output terminology file.

By copying input files and providing them multiple times as inputs, you can
even achieve "weighted" thresholding, so that for example, all terms in one
original input file will pass thresholding, while other files may be filtered.
A simple version of this technique was used above to incorporate translations
from the Gnome terminology PO files without having it affect the terms that
passed the threshold filters. 

--locs-needed
-------------

Rather than requiring that a term appear in multiple input PO or POT files,
this requires that it have been present in multiple source code files, as
evidenced by location comments in the PO/POT sources.

This threshold can be helpful in eliminating over-specialized terminology that
you don't want when multiple PO/POT files are generated from the same sources
(via included header or library files).

Note that some PO/POT files have function names rather than source file names
in the location comments; in this case the threshold will be on multiple
functions, which may need to be set higher to be effective.

Not all PO/POT files contain proper location comments.  If your input files
don't have (good) location comments and the output terminology file is reduced
to zero or very few entries by thresholding, you may need to override the
default value for this threshold and set it to 0, which disables this check.

The setting of the :opt:`--locs-needed` comment has another effect, which is
that location comments in the output terminology file will be limited to twice
that number; a location comment indicating the number of additional locations
not specified will be added instead of the omitted locations.

--fullmsg-needed & --substr-needed
----------------------------------

These two thresholds specify the number of different translation units
(messages) in which a term must appear; they both work in the same way, but the
first one applies to terms which appear as complete translation units in one or
more of the source files (full message terms), and the second one to all other
terms (substring terms).  Note that translations are extracted only for full
message terms; poterminology cannot identify the corresponding substring in a
translation.

If you are working with a single input file without useful location comments,
increasing these thresholds may be the only way to effectively reduce the
output terminology.  Generally, you should increase the :opt:`--substr-needed`
threshold first, as the full message terms are more likely to be useful
terminology.

.. _poterminology#stop_word_files:

Stop word files
===============

Much of the power of poterminology in generating useful terminology files is
due to the default stop word file that it uses.  This file contains words and
regular expressions that poterminology will ignore when generating terms, so
that the output terminology doesn't have tons of useless entries like "the 16"
or "Z".

In most cases, the default stop word list will work well, but you may want to
replace it with your own version, or possibly just supplement or override
certain entries.  The default :doc:`poterminology stopword file
<poterminology_stopword_file>` contains comments that describe the syntax and
operation of these files.

If you want to completely replace the stopword list (for example, if your
source language is French rather than English) you could do it with a command
like this::

  poterminology --stopword-list=stoplist-fr logiciel/ -o glossaire.po

If you merely want to modify the standard stopword list with your own additions
and overrides, you must explicitly specify the default list first::

  poterminology -S /usr/lib/python2.5/site-packages/translate/share/stoplist-en \
    -S my-stoplist po/ -o terminology.po

You can use poterminology :opt:`--help` to see the default stopword list
pathname, which may differ from the one shown above.

Note that if you are using multiple stopword list files, as in the above, they
will all be subject to the same case mapping (fold "Title Case" to lower case
by default) -- if you specify a different case mapping in the second file it
will override the mapping for all the stopword list files.

.. _poterminology#issues:

Issues
======

When using poterminology on Windows systems, file globbing for input is not
supported (unless you have a version of Python built with cygwin, which is not
common).  On Windows, a command like ``poterminology -o test.po podir/\*.po``
will fail with an error "No such file or directory: 'podir\\*.po'" instead of
expanding the podir/\*.po glob expression.  (This problem affects all Translate
Toolkit command-line tools, not just poterminology.)  You can work around this
problem by making sure that the directory does not contain any files (or
subdirectories) that you do not want to use for input, and just giving the
directory name as the argument, e.g. ``poterminology -o test.po podir`` for the
case above.

When using terminology files generated by poterminology as input, a plethora of
translator comments marked with (poterminology) may be generated, with the
number of these increasing on each iteration.  You may wish to run
:doc:`pocommentclean` (or a slightly modified version of it which only removes
(poterminology) comments) on the input and/or output files, especially since
translator comments are displayed as tooltips by Pootle (thankfully, they are
truncated at a few dozen characters).

Default threshold settings may eliminate all output terms; in this case,
poterminology should suggest threshold option settings that would allow output
to be generated (this enhancement is tracked as :issue:`582`).

While poterminology ignores XML/HTML entities and elements and %-style format
strings (for C and Python), it does not ignore all types of "variables" that
may occur, particularly in OpenOffice.org, Mozilla, or Gnome localization
files.  These other types should be ignored as well (this enhancement is
tracked as :issue:`598`).

Terms containing only words that are ignored individually, but not excluded
from phrases (e.g. "you are you") may be generated by poterminology, but aren't
generally useful.  Adding a new threshold option :opt:`--nonstop-needed` could
allow these to be suppressed (this enhancement is tracked as :issue:`1102`).

Pootle ignores parenthetical comments in source text when performing
terminology matching; this allows for terms like "scan (verb)" and "scan
(noun)" to both be provided as suggestions for a message containing "scan."
poterminology does not provide any special handling for these, but it could use
them to provide better handling of different translations for a single term.
This would be an improvement over the current approach, which marks the term
fuzzy and includes all variants, with location information in {} braces in the
automatically extracted translation.

Currently, message context information (PO msgctxt) is not used in any way;
this could provide an additional source of information for distinguishing
variants of the same term.

A single execution of poterminology can only perform automatic translation
extraction for a single target language -- having the ability to handle all
target languages in one run would allow a single command to generate all
terminology for an entire project.  Additionally, this could provide even more
information for identifying variant terms by comparing the number of target
languages that have variant translations.

.. _poterminology#on_single_files:

On single files
===============

If poterminology yields 0 terms from single files, try the following::

  poterminology --locs-needed=0 --inputs-needed=0 --substr-needed=5 -i yourfile.po -o yourfile_term.po

...where "substr-needed" is the number of times a term should occur to be
considered.

