
.. _quoting_and_escaping:

Quoting and Escaping
********************

Different translation :doc:`formats <index>` handle quoting and escaping
strings differently. This is meant to be a common page which outlines the
differences

.. _quoting_and_escaping#po_format:

PO format
=========

Strings are quoted using double quotes. For long strings multiline quotes are
done by opening and closing the quotes on each line. Usually in this case the
first line is left blank. The splitting of strings over lines is transparent
i.e. it does not imply line breaks in the translated strings.

Escaping is done with a backslash. An escaped double quote (``\"``) corresponds
to a double quote in the original string. ``\n`` for newline, ``\t`` for tabs
etc are used. Backslashes can be escaped to to give a native backslash.

See also :wiki:`escaping <guide/translation/escaping>` in the translation
guide.

Example:

.. code-block:: po

  msgid ""
  "This is a long string with a \n newline, a \" double quote, and a \\ backslash."
  "There is no space between the . at the end of the last sentence "
  "and the T at the beginning of this one."

.. _quoting_and_escaping#dtd_format:

DTD format
==========

Strings are quoted using either double or single quotes. The quoting character
may not occur within the string. There is no provision for escaping. XML
entities can be used e.g. ``&apos;`` can be used to denote a single quote
within the single-quoted string.

Some DTD files seem to have backslash-escapes, but these are anomalies: see
`discussion thread on Mozilla l10n-dev
<http://groups.google.com/group/mozilla.dev.l10n/browse_thread/thread/58256c1f59c22798/b4bac2de4182f3e0>`_

.. _quoting_and_escaping#mozilla_properties_format:

Mozilla properties format
=========================

Note that this section does not describe the Java properties files, even though
they are quite similar.

It seems that the literal string ``\n`` (a backslash followed by the character
'n') and ``\t`` and ``\r`` can not be encoded in properties files. This is the
assumption of the toolkit.
