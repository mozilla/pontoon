
.. _rc2po:
.. _po2rc:

rc2po
*****

Converts Windows Resource .rc files to Gettext PO format.

.. _rc2po#usage:

Usage
=====

::

  rc2po [options] <rc> <po>
  po2rc [options] -t <rc> <po> <rc>

Where:

+--------+---------------------------------------------------------------+
| <rc>   | is a valid Windows Resource file or directory of those files  |
+--------+---------------------------------------------------------------+
| <po>   | is a directory of PO or POT files                             |
+--------+---------------------------------------------------------------+

Options (rc2po):

--version           show program's version number and exit
-h, --help          show this help message and exit
--manpage           output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT      read from INPUT in rc format
-x EXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT     write to OUTPUT in po, pot formats
-t TEMPLATE, --template=TEMPLATE  read from TEMPLATE in rc format
-P, --pot    output PO Templates (.pot) rather than PO files (.po)
--charset=CHARSET    charset to use to decode the RC files (default:                        cp1252)
--duplicates=DUPLICATESTYLE
                      what to do with duplicate strings (identical source
                      text): :doc:`merge, msgctxt <option_duplicates>`
                      (default: 'msgctxt')

Options (po2rc):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT  read from INPUT in po, pot formats
-x EXCLUDE, --exclude=EXCLUDE   exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT      write to OUTPUT in rc format
-t TEMPLATE, --template=TEMPLATE  read from TEMPLATE in rc format
-S, --timestamp      skip conversion if the output file has newer timestamp
--charset=CHARSET    charset to use to decode the RC files (default: utf-8)
-l LANG, --lang=LANG  LANG entry
--sublang=SUBLANG     SUBLANG entry (default: SUBLANG_DEFAULT)
--threshold=PERCENT  only convert files where the translation completion is above PERCENT
--fuzzy              use translations marked fuzzy
--nofuzzy            don't use translations marked fuzzy (default)

.. _rc2po#formats_supported:

Formats Supported
=================

.. note:: This implementation is based mostly on observing WINE .rc files,
   these should mimic other non-WINE .rc files.

.. _rc2po#examples:

Examples
========

This example looks at roundtrip of Windows Resource translations as well as
recovery of existing translations.

First we need to create a set of POT files. ::

  rc2po -P lang/ pot/

All .rc files found in the ``lang/`` directory are converted to Gettext POT
files and placed in the ``pot/`` directory.

If you are translating for the first time then you can skip the next step.  If
you need to recovery your existing translations then we do the following::

  rc2po -t lang zu po-zu/

Using the English .rc files found in ``lang`` and your existing Zulu
translation in ``zu`` we create a set of PO files in ``po-zu``.  These will now
have your translations.  Please be aware that in order for the to work 100% you
need to have both English and Zulu at the same revision, if they are not you
will have to review all translations.  Also the .rc files may be in different
encoding, we cannot at the moment process files of different encodings and
assume both are in the same encoding supplied.

You are now in a position to translate your recovered translations or your new
POT files.

Once translated you can convert back as follows::

  po2rc -t lang/ po-zu/ zu/

Your translations found in the Zulu PO directory, ``po-zu``, will be converted
to .rc using the files in ``lang/`` as templates and placing your new
translations in ``zu/``.

To update your translations simply redo the POT creation step and make use of
:doc:`pot2po` to bring your translation up-to-date.

.. _rc2po#issues:

Issues
======

If you are recovering translation using ``rc2po -t en.rc xx.rc xx.po`` then
both en.rc and xx.rc need to be in the same encoding.

There might be problems with MENUs that are deaply nested.
