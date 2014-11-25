
.. _option_duplicates:

--duplicates=DUPLICATESTYLE
***************************

Gettext PO files only allow one message with a common msgid (source string).
Many other formats allow duplicate entries.  To create a valid PO file you need
to merge these duplicate entries into one PO message.  However, this often
negatively affects the roundtrip or is not what is expected by the user.  Thus
we have a number of methods of handling duplicates which we call *duplicate
styles*.

Also affected are conversions in which the source format is empty (allowing
possible translation). As the header in a PO file is identified by an empty
source string, your message will appear to be a duplicate of the header.  In
this case duplicate removal is critical.

Previously the tools used msgid_comment (KDE style comments) to disambiguate
text.  However, with the release of Gettext 0.15, the new msgctxt
disambiguation is now recommended, especially if you wish to use your files
with other Gettext the tools. Many other pieces of software now also support
this feature, and will probably become the best choice for almost all
circumstances.  It is the default in our converters.

.. _option_duplicates#merge:

merge
=====

This is the traditional Gettext approach.  All messages with the same source
string or English string are merged into one PO message.

.. code-block:: po

    #: file1.dtd:instruction_manual
    #: file1.dtd:manual_process
    msgid "Manual"
    msgstr ""

If however the source text is blank (these are often configuration options in
Mozilla) then the *merge* style will use KDE comments as used in the
*msgid_comment* style in order to create unambiguous entries that can still be
used for configuration.

.. code-block:: po

    #: file1.dtd:translators_name
    msgid "_: file1.dtd:translators_name\n"
    msgstr ""

    #: file1.dtd:translators_email
    msgid "_: file1.dtd:translators_email\n"
    msgstr ""

.. _option_duplicates#msgctxt:

msgctxt (default)
=================

This uses the msgctxt feature of Gettext that was introduced with Gettext 0.15.
Some tools might not support it 100%. This option is the default in recent
releases of the Translate Toolkit.

.. code-block:: po

    #: file1.dtd:instruction_manual
    msgctxt "instruction_manual"
    msgid "Manual"
    msgstr ""
     
    #: file1.dtd:manual_process
    msgctxt "manual_process"
    msgid "Manual"
    msgstr ""
