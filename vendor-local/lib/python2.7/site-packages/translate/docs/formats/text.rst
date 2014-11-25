
.. _text:

Simple Text Documents
*********************

The Translate Toolkit can process simple Text files.  This is very useful for
translating installation files and READMEs.  The processing of these files is
performed by the :doc:`txt2po </commands/txt2po>` converter.

In some cases you will need to adjust the source text for the conversion
management to work well.  This is because the text file format support
considered units to be space separated blocks of text.

.. _text#example:

Example
=======

::

  Heading
  =======

  Paragraph One

  Paragraph Two:
  * First bullet
  * Second bullet

This example will result in three units.  The first will include the underline
in the header.  The third will include all the bullet points in one paragraph
together with the paragraph lead in.
