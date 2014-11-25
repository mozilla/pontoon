
.. _poreencode:

poreencode
**********

Takes a directory of existing PO files and converts them to a given encoding.

.. _poreencode#prerequisites:

Prerequisites
=============

GNU Gettext

.. _poreencode#usage:

Usage
=====

::

  poreencode <encoding> <PO directory>

Where:

+--------------+-----------------------------------------------------------+
| encoding     | is the encoding you would like to convert to e.g. UTF-8   |
+--------------+-----------------------------------------------------------+
| PO directory | is a directory of existing PO files                       |
+--------------+-----------------------------------------------------------+

It is best to backup files before the conversion or to perform it against CVS
which prevents a potential loss of data.

.. _poreencode#operation:

Operation
=========

poreencode makes use of the Gettext tool :man:`msgconv` to perform its task.
It traverses the PO directory and finds all PO file.  It uses msgconv to
convert the PO file from its existing encoding to the new encoding.

.. _poreencode#bugs:

Bugs
====

Like most Gettext tools they do a little bit more than documented, msgconv will
decide which strings are in fact fuzzy and delete fuzzy marking -- not a lot
but you do need to diff (this probably related to #, fuzzy entries that are not
placed in the place Gettext expects them).
