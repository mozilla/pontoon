
.. _odf2xliff:
.. _xliff2odf:

odf2xliff and xliff2odf
***********************

Convert OpenDocument (ODF) files to XLIFF localization files. Create translated
ODF files by combining the original ODF files with XLIFF files containing
translations of strings in the original document.

XLIFF is the XML Localization Interchange File Format developed by `OASIS
<https://www.oasis-open.org/committees/tc_home.php?wg_abbrev=xliff>`_ (The
Organization for the Advancement of Structured Information Standards) to allow
translation work to be standardised no matter what the source format and to
allow the work to be freely moved from tool to tool.

If you are more used to software translation or l10n, you might want to read a
bit about :doc:`/guides/document_translation`. This should help you to get the
most out of translating ODF with XLIFF.

.. _odf2xliff#usage:

Usage
=====

::

  odf2xliff [options] <original_odf> <xliff>
  xliff2odf [options] -t <original_odf> <xliff> <translated_odf>

Where:

+------------------+---------------------------------------------------------+
| <original_odf>   | is an ODF document whose strings have to be translated  |
+------------------+---------------------------------------------------------+
| <xliff>          | is an XLIFF file                                        |
+------------------+---------------------------------------------------------+
| <translated_odf> | is an ODF file to generate by replacing the strings in  |
+------------------+---------------------------------------------------------+
|                  | <original_odf> with the translated strings in <xliff>   |
+------------------+---------------------------------------------------------+

Options (odf2xliff):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT   read from INPUT in ODF format
-o OUTPUT, --output=OUTPUT     write to OUTPUT in XLIFF format
-S, --timestamp      skip conversion if the output file has newer timestamp

Options (xliff2odf):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT     read from INPUT in XLIFF formats
-o OUTPUT, --output=OUTPUT  write to OUTPUT in ODF format
-t TEMPLATE, --template=TEMPLATE   read from TEMPLATE in ODF format
-S, --timestamp      skip conversion if the output file has newer timestamp

.. _odf2xliff#examples:

Examples
========

::

  odf2xliff english.odt english_français.xlf

Create an XLIFF file from an ODT file (the source ODF file could also be any of
the other ODF files, including ODS, ODG, etc.). ::

  xliff2odf -t english.odt english_français.xlf français.odt

Using english.odt as the template document, and english_français.xlf as the
file of translations, create a translated file français.odt.

.. _odf2xliff#bugs:

Bugs
====

This filter is not yet extensively used -- we appreciate your feedback.  For
more information on conformance to standards, see the :doc:`/formats/xliff` or
:doc:`/formats/odf` pages.
