
.. _csv2po:
.. _po2csv:

csv2po
******

Convert between CSV (Comma Separated Value) files and the PO format.  This is
useful for those translators who can only use a Spreadsheet, a modern
spreadsheet can open CSV files for editing.  It is also useful if you have
other data such as translation memory in CSV format and you wish to use it with
your PO translations.

If you are starting out with your own CSV files (not created by po2csv), take
note of the assumptions of the column layout explained below.

.. _csv2po#usage:

Usage
=====

::

  csv2po [options] <csv> <po>
  po2csv [options] <po> <csv>

Where:

+--------+----------------------------------------------+
| <csv>  | is a file or directory containing CSV files  |
+--------+----------------------------------------------+
| <po>   | is a file or directory containing PO files   |
+--------+----------------------------------------------+

Options (csv2po):

--version             show program's version number and exit
-h, --help            show this help message and exit
--manpage             output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-iINPUT, --input=INPUT     read from INPUT in csv format
-xEXCLUDE, --exclude=EXCLUDE    exclude names matching EXCLUDE from input paths
-oOUTPUT, --output=OUTPUT   write to OUTPUT in po, pot formats
-tTEMPLATE, --template=TEMPLATE   read from TEMPLATE in pot, po, pot formats
-S, --timestamp       skip conversion if the output file has newer timestamp
--charset=CHARSET     set charset to decode from csv files
--columnorder=COLUMNORDER   specify the order and position of columns (location,source,target)
--duplicates=DUPLICATESTYLE
                      what to do with duplicate strings (identical source
                      text): :doc:`merge, msgctxt <option_duplicates>`
                      (default: 'msgctxt')

Options (po2csv):

--version             show program's version number and exit
-h, --help            show this help message and exit
--manpage             output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-iINPUT, --input=INPUT    read from INPUT in po, pot formats
-xEXCLUDE, --exclude=EXCLUDE   exclude names matching EXCLUDE from input paths
-oOUTPUT, --output=OUTPUT   write to OUTPUT in csv format
-S, --timestamp       skip conversion if the output file has newer timestamp
-P, --pot             output PO Templates (.pot) rather than PO files (.po)
--columnorder=COLUMNORDER    specify the order and position of columns (location,source,target)

.. _csv2po#csv_file_layout:

CSV file layout
===============

The resultant CSV file has the following layout

+--------+-----------------+---------------------------------------------+
| Column | Data            | Description                                 |
+========+=================+=============================================+
|  A     | Location        | All the PO #: location comments.  These are |
|        |                 | needed to reconstruct or merge the CSV back |
|        |                 | into the PO file                            |
+--------+-----------------+---------------------------------------------+
|  B     | Source Language | The msgid or source string                  |
+--------+-----------------+---------------------------------------------+
|  C     | Target Language | The msgstr or target language               |
+--------+-----------------+---------------------------------------------+

.. _csv2po#examples:

Examples
========

These examples demonstrate the use of csv2po::

  po2csv -P pot csv

We use the :opt:`-P` option to recognise POT files found in *pot* and convert
them to CSV files placed in *csv*::

  csv2po csv po

Convert CSV files in *csv* to PO files placed in *po*::

  csv2po --charset=windows-1250 -t pot csv po

User working on Windows will often return files encoded in everything but
Unicode.  In this case we convert CSV files found in *csv* from *windows-1250*
to UTF-8 and place the correctly encoded files in *po*.  We use the templates
found in *pot* to ensure that we preserve formatting and other data.  Note that
UTF-8 is the only available destination encoding.

::

  csv2po --columnorder=location,target,source fr.csv fr.po

In case the CSV file has the columns in a different order you may use
:option:`--columnorder`.


.. _csv2po#bugs:

Bugs
====

* Translation comments #[space] and KDE comments _: are not available in CSV
  mode which effects the translators effectiveness
* Locations #: that are not conformant to PO (i.e. have spaces) will get messed
  up by PO tools.
