
.. _popuretext:

popuretext
**********

Extracts all the source text from a directory of POT files or the target text
from a directory of PO files, removing PO headers and optionally the
accelerator keys.

If you want to use other tools to analyse the text within a translation
project, then this is the tool for you.  For example, you can use it to
calculate word frequencies to create an initial glossary based on the pure
source text.

.. _popuretext#prerequisites:

Prerequisites
=============

* GNU Gettext
* sed

.. _popuretext#usage:

Usage
=====

::

  popuretext <-P pot-dir|po-dir> <file.txt> [accelerator]

Where:

+--------------+-----------------------------------------------------------+
| pot-dir      | a directory containing POT files                          |
+--------------+-----------------------------------------------------------+
| po-dir       | a directory containing PO files                           |
+--------------+-----------------------------------------------------------+
| file.txt     | file that contains the output text                        |
+--------------+-----------------------------------------------------------+
| accelerator  | optional: accelerator marker to be removed from the text  |
+--------------+-----------------------------------------------------------+

.. _popuretext#examples:

Examples
========

::

  popuretext -P pot pot.txt '&'

Extract all the source text from the *pot* directory and place it in the
*pot.txt* file removing all occurrences of the ``&`` accelerator. ::

  popuretext af af.txt

Extract all target text from the Afrikaans files in the *af* directory, placing
the extracted text in *af.txt*.  In this case we are not filtering any
accelerator characters.
