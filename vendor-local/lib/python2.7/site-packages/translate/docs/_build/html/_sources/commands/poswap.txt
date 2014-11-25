
.. _poswap:

poswap
******

This tool builds a new translation file with the target text (translation) of
the input file(s) as source language of the output file it creates.

This makes it possible to have French as the source file for translation,
rather than English.  Note that this requires no change in the software project
and is only a manipulation of the strings in the existing files. The only
requirement for this tool is a French translation.

It can also be used to convert translatable files that use logical IDs instead
of source text into a format usable by human localisers.

.. _poswap#usage:

Usage
=====

::

  poswap [options] <newsource> [-t current] <new>

Where:

+-------------+---------------------------------------------------------+
| <newsource> | is the translations (preferably 100% translated) of the |
|             | preferred source language (like French)                 |
+-------------+---------------------------------------------------------+
| <current>   | is the (optional) current English based translation in  |
|             | your intended target language                           |
+-------------+---------------------------------------------------------+
| <new>       | is the intended output file / directory                 |
+-------------+---------------------------------------------------------+

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
-tTEMPLATE, --template=TEMPLATE   read from TEMPLATE in po, pot formats
--reverse  Do the inverse operation (converting back to a normal English based file). See the examples.

.. _poswap#examples:

Examples
========

Ensure that the two po files / directories correspond 100% to the same pot file
before using this.

To start a fresh Afrikaans (af) translation from Dutch (nl)::

    poswap nl.po nl-af.po

This initialises a new, empty file nl-af.po with Dutch as the source language.

To change the nl-af.po file back to the expected English based af.po::

    poswap --reverse nl.po -t nl-af.po af.po

To translate Kurdish (ku) through French (fr)::

    poswap -i fr/ -t ku/ -o fr-ku/

This will take the existing (English based) Kurdish translation in ku/ and
produce files in fr-ku with French as the source language and Kurdish as the
target language.

To convert the fr-ku files back to en-ku::

    poswap --reverse -i fr/ -t fr-ku/ -o en-ku/

This recreates the English based Kurdish translation from the French based
files previously created in fr-ku/.

.. _poswap#issues:

Issues
======

* Behaviour is undetermined if the two files don't match 100%. If PO files are
  based in the same template, there should be no problem.
* We should probably be doing fuzzy matching in future to ease the migration
  over the lifetime of a changing French translation.
