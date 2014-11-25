
.. _qt_phrase_book:
.. _qph:

Qt Phrase Book (.qph)
*********************

.. versionadded:: 1.2

Qt Linguist allows a translator to collect common phrases into a phrase book.
This plays a role of glossary lookup as opposed to translation memory.

.. _qt_phrase_book#conformance:

Conformance
===========

There is no formal definition of the format, although it follows a simple
structure

.. code-block:: xml

  <!DOCTYPE QPH><QPH>
    <phrase>
      <source>Source</source>
      <target>Target</target>
      <definition>Optional definition</definition>
    </phrase>
  </QPH>

.. _qt_phrase_book#missing_features:

Missing features
================

There are no missing features in our support in the toolkit.  The only slight
difference are:

* We don't focus on adding and removing items, just updating and reading
* Comments are not properly escaped on reading, they might be on writing
* An XML header is output on writing while it seems that no files in the wild
  contain an XML header.
* The ``<definition>`` is aimed at users, the toolkits addnote feature focuses
  on programmer, translators, etc comments while there is really only one
  source of comments in a .qph.  This causes duplication on the offline editor.
