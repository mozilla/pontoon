
.. _pogrep:

pogrep
******

The pogrep tool extracts messages that match a regular expression into a new
set of PO files that can be examined, edited and corrected.  These corrections
can then be merged using :doc:`pomerge`.

.. _pogrep#usage:

Usage
=====

::

  pogrep [options] <in> <out>

Where:

+------------+-------------------------------------------------------------+
| <in>/<out> | *In* and *out* are either directories or files.  *Out* will |
|            | contain PO/XLIFF files with only those messages that match  |
|            | the regular expression that was you searched for.           |
+------------+-------------------------------------------------------------+

Options:

--version             show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-iINPUT, --input=INPUT   read from INPUT in po, pot, xlf formats (XLIFF since version 1.0)
-xEXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-oOUTPUT, --output=OUTPUT     write to OUTPUT in po, pot, xlf formats (XLIFF since version 1.0)
--search=SEARCHPARTS  searches the given parts (source, target, notes, locations)
-I, --ignore-case    ignore case distinctions
-e, --regexp         use regular expression matching
-v, --invert-match   select non-matching lines
--accelerator=ACCELERATORS
                      ignores the given :doc:`accelerator characters <option_accelerator>` when matching
-k, --keep-translations
                      always extract units with translations

.. _pogrep#example:

Example
=======

::

  pogrep --accelerator="_" --search msgid -I -e "software|hardware" only-zu only-zu-check

Search for the words "software" or "hardware" in the msgid field.  Ignore case
(:opt:`-I`) and treat the underscore (_) character as an accelerator key.
Search through all PO files in the directory "only-zu" and place any matches in
PO files in the directory "only-zu-check".  This would be useful to run if you
know that the word for software and hardware has been changed during the course
of translation and you want to check and correct all these instances. ::

  pogrep --search=msgid -e '^\w+(\s+\w+){0,3}$' -i templates -o short-words

Find all messages in the *templates* directory that have between 1 and 4 words
and place them in *short-words*.  Use this if you want to see quick results by
translating messages that are most likely menu entries or dialogue labels. ::

  pogrep --search=msgstr -I -e "Ifayile" zu zu-check

Search all translations for the occurrence of *Ifayile*.  You would use this to
check if words have been used correctly.  Useful if you find problematic use of
the same word for different concepts.  You can use :doc:`pocompendium` to find
these conflicts.

.. _pogrep#notes:

Notes
=====

.. _pogrep#unicode_normalization:

Unicode normalization
---------------------

pogrep will normalize Unicode strings.  This allows you to search for strings
that contain the same character but that are using precomposed Unicode
characters or which are composed using another composition recipe.  While an
individual user will in all likelihood only compose characters in one way,
normalization ensures that data created in a team setting can be shared.

.. _pogrep#further_reading:

Further reading
===============
Here is a blog post explaining how pogrep can be used to do more targeted
localisation of GNOME:
http://translate.org.za/blogs/friedel/en/content/better-lies-about-gnome-localisation

