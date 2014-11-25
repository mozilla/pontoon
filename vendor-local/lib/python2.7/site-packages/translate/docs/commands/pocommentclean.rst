
.. _pocommentclean:

pocommentclean
**************

pocommentclean will remove all translator comments from a directory of PO
files.

.. _pocommentclean#prerequisites:

Prerequisites
=============

* :man:`sed`

.. _pocommentclean#usage:

Usage
=====

::

  pocommentclean [--backup] <po>

Where:

+-----+-------------------------------------------------------------+
| po  | is a directory of existing PO files that you want to clean  |
+-----+-------------------------------------------------------------+

Options:

--backup  Create a backup file for each PO file converted, .po.bak

.. _pocommentclean#operation:

Operation
=========

Using sed pocommentclean will delete all lines starting with # but which are
not standard Gettext PO format lines.  So it won't delete developer comments
(#.), obsolete messages (#~), flags (#,) or locations (#:).

.. _pocommentclean#bugs:

Bugs
====

pocommentclean cannot clean individual PO files, it only cleans directories
