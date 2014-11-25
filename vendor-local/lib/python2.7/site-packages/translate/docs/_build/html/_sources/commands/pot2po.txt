
.. _pot2po:

pot2po
******

Convert a Gettext PO Template file to a PO file and merge in existing
translations if they are present. A translation memory (compendium) can also be
used for fuzzy matching. This corresponds to a large extent with the program
"msgmerge" from the gettext package.

.. _pot2po#usage:

Usage
=====

::

  pot2po [options] <pot> <po>

Where:

+--------+---------------------------------------------------------+
| <pot>  | is a PO Template (POT) file or directory of POT files   |
+--------+---------------------------------------------------------+
| <po>   | is a PO file or a directory of PO files                 |
+--------+---------------------------------------------------------+

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
-tTEMPLATE, --template=TEMPLATE   read from TEMPLATE in po, pot formats (old translations)
-S, --timestamp      skip conversion if the output file has newer timestamp
-P, --pot            output PO Templates (.pot) rather than PO files (.po)
--tm=TM              The file to use as translation memory when fuzzy matching
-sMIN_SIMILARITY, --similarity=MIN_SIMILARITY   The minimum similarity for inclusion (default: 75%)
--nofuzzymatching    Disable all fuzzy matching

.. _pot2po#examples:

Examples
========

::

  pot2po -t zu-1.0.1 pot-2.0.2 zu-2.0.2

Here we are initialising the PO files in *zu-2.0.2* based on the POT files in
*pot-2.0.2*.  We are using the old translations in *zu-1.0.1* as templates so
that we can reuse our existing translations in the new files.

If the POT files have undergone major reshuffling then you may want to use
:doc:`pomigrate2` which can now use pot2po as its merging backend.  pomigrate2
will do its best to migrate your files to the correct locations before merging.
It will also make make use of a compendium if requested.::

  pot2po --tm=compendium.po --similarity=60 -t xh-old pot xh-new

With this update we are using *compendium.po* as a translations memory (you can
make use of other files such as TMX, etc).  We will accept any match that
scores above *60%*.

.. _pot2po#merging:

Merging
=======

It helps to understand when and how pot2po will merge. The default is to follow
msgmerge's behaviour but we add some extra features with fuzzy matching:

* If everything matches we carry that across
* We can resurrect obsolete messages for reuse
* Messages no longer used are made obsolete
* If we cannot find a match we will first look through the current and obsolete
  messages and then through any global translation memory
* Fuzzy matching makes use of the :doc:`/commands/levenshtein_distance`
  algorithm to detect the best matches

.. _pot2po#performance:

Performance
===========

Fuzzy matches are usually of good quality. Installation of the
`python-Levenshtein <https://pypi.python.org/pypi/python-Levenshtein>`_ package
will speed up fuzzy matching. Without this a Python based matcher is used which
is considerably slower.

.. _pot2po#bugs:

Bugs
====

* :doc:`pomerge` and pot2po should probably become one.

