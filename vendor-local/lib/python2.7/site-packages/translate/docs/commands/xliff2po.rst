
.. _xliff2po:
.. _po2xliff:

xliff2po
********

Converts XLIFF localization files to Gettext PO files.  XLIFF is the XML
Localization Interchange File Format developed by `OASIS
<https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=xliff>`_
(Organization for the Advancement of Structured Information Standards) to allow
translation work to be standardised no matter what the source format and to
allow the work to be freely moved from tool to tool.

.. _xliff2po#usage:

Usage
=====

::

  po2xliff [options] <po> <xliff>
  xliff2po [options] <xliff> <po>

Where:

+----------+-----------------------------------------------+
| <po>     | is a PO file or directory of PO files         |
+----------+-----------------------------------------------+
| <xliff>  | is an XLIFF file or directory of XLIFF files  |
+----------+-----------------------------------------------+

Options (xliff2po):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-iINPUT, --input=INPUT   read from INPUT in xliff format
-xEXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-oOUTPUT, --output=OUTPUT     write to OUTPUT in po, pot formats
-S, --timestamp       skip conversion if the output file has newer timestamp
-P, --pot            output PO Templates (.pot) rather than PO files (.po)
--duplicates=DUPLICATESTYLE
                      what to do with duplicate strings (identical source
                      text): :doc:`merge, msgctxt <option_duplicates>`
                      (default: 'msgctxt')

Options (po2xliff):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-iINPUT, --input=INPUT     read from INPUT in po, pot formats
-xEXCLUDE, --exclude=EXCLUDE   exclude names matching EXCLUDE from input paths
-oOUTPUT, --output=OUTPUT  write to OUTPUT in xliff format
-tTEMPLATE, --template=TEMPLATE   read from TEMPLATE in xliff format
-S, --timestamp      skip conversion if the output file has newer timestamp
-P, --pot            output PO Templates (.pot) rather than PO files (.po)

.. _xliff2po#examples:

Examples
========

::

  xliff2po -P xliff pot

Create POT files from the XLIFF files found in directory *xliff* and output
them to the directory *pot*

::

  po2xliff xh xh-xlf

Convert the Xhosa PO files in *xh* to XLIFF and place them in *xh-xlf*

.. _xliff2po#bugs:

Bugs
====

This filter is not yet extensively used... expect bugs.  See :doc:`XLIFF
</formats/xliff>` to see how well our implementation conforms to the standard.

The PO plural implementation is still very new and needs active testing.
