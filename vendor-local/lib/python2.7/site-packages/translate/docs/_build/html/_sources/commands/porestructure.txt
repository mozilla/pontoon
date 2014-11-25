
.. _porestructure:

porestructure
*************

porestructure takes the PO files output by :doc:`poconflicts` (a flat
structure), and recreates the directory structure according to the poonflict
location comments found in each PO message. After being restructured, the
messages in the resulting directory structure can be merged back using
:doc:`pomerge`.

Since poconflicts adds conflicting messages, from many different PO files, into
a single PO file, the original structure of the files and directories are lost
and the new PO files are output to a single directory. The original structure
information is left in "(pofilter)" comments for each PO element.

.. _porestructure#usage:

Usage
=====

::

  porestructure [options] <conflicts> <po>

Where:

+-------------+-----------------------------------------------------------+
| <conflicts> | is a directory containing one the corrected output from   |
|             | poconflict                                                |
+-------------+-----------------------------------------------------------+
| <po>        | is an output directory to write the restructured files to |
+-------------+-----------------------------------------------------------+

Options:

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-iINPUT, --input=INPUT   read from INPUT in po format
-xEXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-oOUTPUT, --output=OUTPUT  write to OUTPUT in po format

.. _porestructure#examples:

Examples
========

The documentation for poconflicts has :ref:`poconflicts#examples` for the
complete process using poconflict, porestructure, and pomerge.

.. _porestructure#bugs:
