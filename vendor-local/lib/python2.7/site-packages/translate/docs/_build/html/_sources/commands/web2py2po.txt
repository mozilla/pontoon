
.. _py2web2po:
.. _po2web2py:

web2py2po
*********

Converts web2py translation files to PO files and vice versa.

`Web2py <http://web2py.com/>`_, formerly known as Gluon) is an open-source,
Python-based web application framework by Massimo Di Pierro (inspired by Django
and Rails).

Web2py uses an internal localization engine based on Python dictionaries, which
is applied with the T() lookup function. Web2py provides a built-in translation
interface for the T()-engine, which is excellent for rapid application
development.

On the other hand, for collaboration and workflow control in a wider community
you might probably rather want to use Pootle, Launchpad or similar facilities
for translation, thus need to transform the web2py dictionaries into PO files
and vice versa. And exactly that is what the web2py2po converters are good for.

.. _py2web2po#usage:

Usage
=====

::

  web2py2po [options] <web2py> <po>
  po2web2py [options] <po> <web2py>

Where:

+----------+--------------------------------------------------------+
| <web2py> | is a valid web2py translation file                     |
+----------+--------------------------------------------------------+
| <po>     | is a PO or POT file or a directory of PO or POT files  |
+----------+--------------------------------------------------------+

Options (web2py2po):

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
-S, --timestamp       skip conversion if the output file has newer timestamp
--duplicates=DUPLICATESTYLE
                      what to do with duplicate strings (identical source
                      text): :doc:`merge, msgctxt <option_duplicates>`
                      (default: 'msgctxt')

Options (po2web2py):

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
-S, --timestamp      skip conversion if the output file has newer timestamp
--threshold=PERCENT  only convert files where the translation completion is above PERCENT
--fuzzy              use translations marked fuzzy
--nofuzzy            don't use translations marked fuzzy (default)

.. _py2web2po#notes:

Notes
=====

**Handling of blanks/untranslated messages:**

Untranslated messages in the web2py translation files are usually marked with a
leading ``%%"*** "%%``, so:

* All target strings from the web2py sources with a leading ``%%"*** "%%`` are
  inserted as blank msgstr's into the PO result (web2py2po)
* Blank msgstr's from the PO file will get the msgid string with a leading
  ``%%"*** "%%`` as target string in the web2py result (po2web2py)
