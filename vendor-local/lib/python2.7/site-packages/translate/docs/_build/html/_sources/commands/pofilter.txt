
.. _pofilter:

pofilter
********

Pofilter allows you to run a :doc:`number of checks <pofilter_tests>` against
your PO, XLIFF or TMX files.  These checks are designed to pick up problems
with capitalisation, accelerators, variables, etc.  Those messages that fail
any of the checks are output and marked so that you can correct them.

Use ``pofilter -l`` to get a list of available checks.

Once you have corrected the errors in your PO files you can merge the
corrections into your existing translated PO files using :doc:`pomerge`.

.. _pofilter#usage:

Usage
=====

::

  pofilter [options] <in> <out>

Where:

+-------+-------------------------------------------------------------------+
| <in>  | the input file or directory which contains PO or XLIFF files      |
+-------+-------------------------------------------------------------------+
| <out> | the output file or directory that contains PO or XLIFF files that |
|       | fail the various tests                                            |
+-------+-------------------------------------------------------------------+

Options:

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-iINPUT, --input=INPUT   read from INPUT in pot, po, xlf, tmx formats
-xEXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-oOUTPUT, --output=OUTPUT  write to OUTPUT in po, pot, xlf, tmx formats
-l, --listfilters    list filters available
--review             include elements marked for review (default)
--noreview           exclude elements marked for review
--fuzzy              include elements marked fuzzy (default)
--nofuzzy            exclude elements marked fuzzy
--header             include a PO header in the output (always the case since version 1.6)
--nonotes            don't add notes about the errors (since version 1.3)
--autocorrect        output automatic corrections where possible rather than describing issues
--language=LANG      set target language code (e.g. af-ZA) [required for spell check]. This will help to make pofilter aware of the conventions of your language
--openoffice         use the standard checks for OpenOffice translations
--libreoffice        use the standard checks for LibreOffice translations
--mozilla            use the standard checks for Mozilla translations
--drupal            use the standard checks for Drupal translations
--gnome              use the standard checks for Gnome translations
--kde                use the standard checks for KDE translations
--wx                 use the standard checks for wxWidgets translations -- identical to --kde
--excludefilter=FILTER  don't use FILTER when filtering
-tFILTER, --test=FILTER  only use test FILTERs specified with this option when filtering
--notranslatefile=FILE   read list of untranslatable words from FILE (must not be translated)
--musttranslatefile=FILE  read list of translatable words from FILE (must be translated)
--validcharsfile=FILE  read list of all valid characters from FILE (must be in UTF-8)

.. _pofilter#example:

Example
=======

Here are some examples to demonstrate how to use pofilter::

  pofilter --openoffice af af-check

Use the default settings (accelerator and variables) for OpenOffice.org.  Check
all PO files in *af* and output any messages that fail the check in *af-check*
(create the directory if it does not already exist). ::

  pofilter -t isfuzzy -t untranslated zu zu-check

Only run the *isfuzzy* and *untranslated* checks, this will extract all
messages that are either fuzzy or untranslated. ::

  pofilter --excludefilter=simplecaps --nofuzzy nso nso-check

Run all filters except *simplecaps*.  You might want to do this if your
language does not make use of capitalisation or if the test is creating too
many false positives.  Also only run the checks against messages that are not
marked fuzzy.  This is useful if you have already marked problem strings as
fuzzy or you know that the fuzzy strings are bad, with this option you don't
have to see the obviously wrong messages. ::

  pofilter --language=fr dir dir-check

Tell pofilter that you are checking French translations so that it can take the
conventions of the language into account (for things like punctuation, spacing,
quoting, etc.) It will also disable some tests that are not meaningful for your
language, like capitalisation checks for languages that don't have capital
letters. ::

  pofilter --excludefilter=untranslated

Tell pofilter not to complain about your untranslated units. ::

  pofilter -l

List all the available checks.

.. _pofilter#bugs:

Bugs
====

There are minor bugs in the filters.  Most relate to false positives, corner
cases or minor changes for better fault description.
