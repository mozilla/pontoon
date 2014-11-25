
.. _utx:

Universal Terminology eXchange (UTX)
************************************

.. versionadded:: 1.9

UTX is implemented by the Asia-Pacific Association for Machine Translation

.. _utx#resources:

Resources
=========

* `UTX site <http://www.aamt.info/english/utx/index.htm>`_
* `Current Specification <http://www.aamt.info/english/utx/#Download>`_
  (implementation is based on UTX 1.0 which is no longer available)

.. _utx#conformance:

Conformance
===========

The Translate Toolkit implementation of UTX can correctly:

* Handle the header.  Although we don't generate the header at the moment
* Read any of the standard columns and optional columns.  Although we can
  access these extra columns we don't do much with them.

Adjustments and not implemented features where the spec is not clear:

* We do not implement the "#." comment as we need clarity on this
* The "<space>" override for no part of speech is not implemented
* The spec calls for 2 header lines, while examples in the field have 2-3
  lines.  We can read as many as supplied but assume the last header line is
  the column titles
* We remove # from all field line entries, some examples in the field have
  ``#tgt`` as a column name
