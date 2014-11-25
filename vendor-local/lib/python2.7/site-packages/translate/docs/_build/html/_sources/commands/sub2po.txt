
.. _sub2po:
.. _po2sub:

sub2po
******

sub2po allows you to use the same principles of PO files with
:doc:`/formats/subtitles`. In PO only items that change are marked fuzzy and
only new items need to be translated, unchanged items remain unchanged for the
translation.

.. _sub2po#usage:

Usage
=====

::

  sub2po [options] <foo.srt> <foo.po>
  po2sub [options] [-t <foo.srt>] <XX.po> <foo-XX.srt>

Where:

+------------+---------------------------------------------------+
| foo.srt    | is the input subtitle file                        |
+------------+---------------------------------------------------+
| foo.po     | is an empty PO file that may be translated        |
+------------+---------------------------------------------------+
| XX.po      | is a PO file translated into the XX language      |
+------------+---------------------------------------------------+
| foo-XX.srt | is the foo.srt file translated into language XX   |
+------------+---------------------------------------------------+

Options (sub2po):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-iINPUT, --input=INPUT    read from INPUT in .srt format
-xEXCLUDE, --exclude=EXCLUDE   exclude names matching EXCLUDE from input paths
-oOUTPUT, --output=OUTPUT  write to OUTPUT in po, pot formats
-S, --timestamp       skip conversion if the output file has newer timestamp
-P, --pot            output PO Templates (.pot) rather than PO files (.po)
--duplicates=DUPLICATESTYLE
                      what to do with duplicate strings (identical source
                      text): :doc:`merge, msgctxt <option_duplicates>`
                      (default: 'msgctxt')

Options (po2sub):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-iINPUT, --input=INPUT    read from INPUT in po, pot formats
-xEXCLUDE, --exclude=EXCLUDE   exclude names matching EXCLUDE from input paths
-oOUTPUT, --output=OUTPUT   write to OUTPUT in srt format
-tTEMPLATE, --template=TEMPLATE   read from TEMPLATE in txt format
-S, --timestamp      skip conversion if the output file has newer timestamp
--threshold=PERCENT  only convert files where the translation completion is above PERCENT
--fuzzy              use translations marked fuzzy
--nofuzzy            don't use translations marked fuzzy (default)

.. _sub2po#examples:

Examples
--------

To create the POT files is simple::

  sub2po -P SUBTITLE_FILE subtitles.pot

A translator would copy the POT file to their own PO file and then create
translations of the entries. If you wish to create a PO file and not a POT file
then leave off the :opt:`-P` option.

To convert back::

  po2sub -t SUBTITLE_FILE   subtitles-XX.po  subtitles-XX.srt

.. _sub2po#translating:

Translating
-----------

Translate as normal. However, see the issues mentioned at
:doc:`/formats/subtitles`.

.. _sub2po#bugs:

Bugs
----
There might be some issues with encodings, since the srt files don't specify
them. We assume files to be encoded in UTF-8, so a conversion should solve this
easily. Note that most of the handling of the srt files come from gaupol.

