
.. _json2po:
.. _po2json:

json2po
*******

Converts .json files to Gettext PO format.

.. _json2po#usage:

Usage
=====

::

  json2po [options] <json> <po>
  po2json [options] -t <json> <po> <json>

Where:

+---------+---------------------------------------------------+
| <json>  | is a valid .json file or directory of those files |
+---------+---------------------------------------------------+
| <po>    | is a directory of PO or POT files                 |
+---------+---------------------------------------------------+

Options (json2po):

--version           show program's version number and exit
-h, --help          show this help message and exit
--manpage           output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT      read from INPUT in JSON format
-x EXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT     write to OUTPUT in po, pot formats
-t TEMPLATE, --template=TEMPLATE  read from TEMPLATE in JSON format
-S, --timestamp       skip conversion if the output file has newer timestamp
-P, --pot    output PO Templates (.pot) rather than PO files (.po)
--filter=FILTER  leaves to extract e.g. 'name,desc': (default: extract everything)
--duplicates=DUPLICATESTYLE
                      what to do with duplicate strings (identical source
                      text): :doc:`merge, msgctxt <option_duplicates>`
                      (default: 'msgctxt')

Options (po2json):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT  read from INPUT in po, pot formats
-x EXCLUDE, --exclude=EXCLUDE   exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT      write to OUTPUT in JSON format
-t TEMPLATE, --template=TEMPLATE  read from TEMPLATE in JSON format
-S, --timestamp      skip conversion if the output file has newer timestamp
--threshold=PERCENT  only convert files where the translation completion is above PERCENT
--fuzzy              use translations marked fuzzy
--nofuzzy            don't use translations marked fuzzy (default)

.. _json2po#examples:

Examples
========

This example looks at roundtrip of .json translations as well as recovery of
existing translations.

First we need to create a set of POT files. ::

  json2po -P json/ pot/

All .json files found in the ``json/`` directory are converted to Gettext POT
files and placed in the ``pot/`` directory.

If you are translating for the first time then you can skip the next step.  If
you need to recover your existing translations then we do the following::

  json2po -t lang/ zu/ po-zu/

Using the English .json files found in ``lang/`` and your existing Zulu
translation in ``zu/`` we create a set of PO files in ``po-zu/``.  These will
now have your translations.  Please be aware that in order for the to work 100%
you need to have both English and Zulu at the same revision. If they are not,
you will have to review all translations.

You are now in a position to translate your recovered translations or your new
POT files.

Once translated you can convert back as follows::

  po2json -t lang/ po-zu/ zu/

Your translations found in the Zulu PO directory, ``po-zu/``, will be converted
to .json using the files in ``lang/`` as templates and placing your newly
translated .json files in ``zu/``.

To update your translations simply redo the POT creation step and make use of
:doc:`pot2po` to bring your translation up-to-date.
