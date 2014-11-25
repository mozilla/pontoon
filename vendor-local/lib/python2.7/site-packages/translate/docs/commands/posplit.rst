
.. _posplit:

posplit
*******

Takes an existing PO file and splits it into three components: translated,
untranslated and fuzzy.  This is useful for reviewing translations or for
extracting good translations from a compendium file.

Note that the input file is removed by the script (until version 1.9.1). The
generated output files can be combined again with msgcat.

.. _posplit#prerequisites:

Prerequisites
=============

GNU Gettext

.. _posplit#usage:

Usage
=====

::

  posplit ./file.po

Where:

+-----------+------------------------------------------+
| file.po   | is an existing PO file or PO compendium  |
+-----------+------------------------------------------+

.. _posplit#bugs:

Bugs
====

* Some relative path bugs thus the need for ./ before file.po.
* Until version 1.9.1, the original input file was removed, :issue:`2006`.

