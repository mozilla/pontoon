
.. _tiki2po:
.. _po2tiki:

tiki2po
*******

Converts `TikiWiki <http://tikiwiki.org>`_ language.php files to Gettext PO
format.

.. _tiki2po#usage:

Usage
=====

::

  tiki2po [options] <tiki> <po>
  po2tiki [options] <po> <tiki>

Where:

+----------+--------------------------------------------+
| <tiki>   | is a valid language.php file for TikiWiki  |
+----------+--------------------------------------------+
| <po>     | is a PO file                               |
+----------+--------------------------------------------+

Options (tiki2po):

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
--include-unused      When converting, include strings in the "unused" section?

Options (po2tiki):

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

.. _tiki2po#examples:

Examples
========

These examples demonstrate the use of tiki2po::

  tiki2po language.php language.po

Convert the tiki language.php file to .po::

  po2tiki language.po language.php

Convert a .po file to a tiki language.php file

.. _tiki2po#notes:

Notes
=====

* Templates are not currently supported.
