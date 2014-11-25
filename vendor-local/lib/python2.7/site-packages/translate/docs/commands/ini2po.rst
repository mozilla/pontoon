
.. _ini2po:
.. _po2ini:

ini2po
******

Converts .ini files to Gettext PO format.

.. _ini2po#usage:

Usage
=====

::

  ini2po [options] <ini> <po>
  po2ini [options] -t <ini> <po> <ini>

Where:

+---------+---------------------------------------------------+
| <ini>   | is a valid .ini file or directory of those files  |
+---------+---------------------------------------------------+
| <po>    | is a directory of PO or POT files                 |
+---------+---------------------------------------------------+

Options (ini2po):

--version           show program's version number and exit
-h, --help          show this help message and exit
--manpage           output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT      read from INPUT in php format
-x EXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT     write to OUTPUT in po, pot formats
-t TEMPLATE, --template=TEMPLATE  read from TEMPLATE in php format
-S, --timestamp       skip conversion if the output file has newer timestamp
-P, --pot    output PO Templates (.pot) rather than PO files (.po)
--duplicates=DUPLICATESTYLE
                      what to do with duplicate strings (identical source
                      text): :doc:`merge, msgctxt <option_duplicates>`
                      (default: 'msgctxt')

Options (po2ini):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT  read from INPUT in po, pot formats
-x EXCLUDE, --exclude=EXCLUDE   exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT      write to OUTPUT in php format
-t TEMPLATE, --template=TEMPLATE  read from TEMPLATE in php format
-S, --timestamp      skip conversion if the output file has newer timestamp
--threshold=PERCENT  only convert files where the translation completion is above PERCENT
--fuzzy              use translations marked fuzzy
--nofuzzy            don't use translations marked fuzzy (default)

.. _ini2po#formats_supported:

Formats Supported
=================

INI files need to be organized into separate languages per file and in the
following format::

    [Section]
      ; a comment
      a = a string

Comment marked with the hash symbol (#) are also allowed, and the colon (:) is
also accepted as key-value delimiter::

    [Section]
      # another comment
      b : a string

This variants in comment marks and key-value delimiters can be mixed in one
single INI file::

    [Section]
    ; a comment
    a = a string
    # another comment
    b : a string
    c:'other example with apostrophes'
    d:"example with double quotes"

The spacing between the key-value delimiter and the key, and the between the
value and the key-value delimiter is not important since the converter
automatically strips the blank spaces.

.. note:: A section must be present at the file beginning in order to get
   ini2po working properly. You may add it by hand at the file beginning.

.. note:: Strings marked with double quotes and/or apostrophes will carry
   these quotation marks to the generated .po file, so they will appear like:

   .. code-block:: po

       #: [Section]c
       msgid "'other example with apostrophes'"
       msgstr ""
       
       #: [Section]d
       msgid "\"example with double quotes\""
       msgstr ""

.. _ini2po#examples:

Examples
========

This example looks at roundtrip of .ini translations as well as recovery of
existing translations.

First we need to create a set of POT files. ::

  ini2po -P ini/ pot/

All .ini files found in the ``ini/`` directory are converted to Gettext POT
files and placed in the ``pot/`` directory.

If you are translating for the first time then you can skip the next step.  If
you need to recover your existing translations then we do the following::

  ini2po -t lang/ zu/ po-zu/

Using the English .ini files found in ``lang/`` and your existing Zulu
translation in ``zu/`` we create a set of PO files in ``po-zu/``.  These will
now have your translations.  Please be aware that in order for the to work 100%
you need to have both English and Zulu at the same revision. If they are not,
you will have to review all translations.

You are now in a position to translate your recovered translations or your new
POT files.

Once translated you can convert back as follows::

  po2ini -t lang/ po-zu/ zu/

Your translations found in the Zulu PO directory, ``po-zu/``, will be converted to .ini using the files in ``lang/`` as templates and placing your newly translated .ini files in ``zu/``.

To update your translations simply redo the POT creation step and make use of :doc:`pot2po` to bring your translation up-to-date.

.. _ini2po#issues:

Issues
======

We do not extract comments from .ini files.  These are sometimes needed as developers provide guidance to translators in these comments.
