
.. _omegat_glossary:

OmegaT glossary
***************

.. versionadded:: 1.5.1

OmegaT allows a translator to create a terminology list of glossary files.  It
uses this file to provide its glossary matches to the OmegaT users.

.. _omegat_glossary#format_specifications:

Format specifications
=====================

The glossary files is a tab delimeted files with three columns:

#. source
#. target
#. comment

The files is stored in the system locale if the files extension is ``.txt`` or
in UTF-8 if the file extension is ``.utf8``.

.. _omegat_glossary#conformance:

Conformance
===========

The implementation can load files in UTF-8 or the system encoding.

.. _omegat_glossary#issues:

Issues
======

* There has not been extensive testing on system encoded files and there are
  likely to be issues in these files for encodings that fall outside of common
  ASCII characters.
* Files with additional columns are read correctly but cannot be written.

