
.. _po:

PO Files
********
PO files use the file format of the Gettext tools.

.. seealso:: `Gettext manual <http://www.gnu.org/software/gettext/>`_


.. _po#supported_features:

Supported Features
==================

* Headers
* Language header (since gettext version 0.17)
* Plural forms and plural form handling
* Message context

  .. code-block:: po

    msgctxt "noun"
    msgid "View"
    msgstr ""

* Normal comments

  .. code-block:: po

    # this is another comment

* Automatic comments

  .. code-block:: po

    #. comment extracted from the source code

* Source location comments

  .. code-block:: po

    #: sourcefile.xxx:35

* Typecomments

  .. code-block:: po

    #, fuzzy

* Msgidcomments, also known as KDE style comments as they are used by KDE for
  message disambiguation and comments to translators.

  .. note:: Support for this is being phased out in favor of ``msgctxt``.

  .. code-block:: po

    msgid "_: comment\n"
    "translation"

* Obsolete messages

  .. code-block:: po

    #~ msgid "Blah"
    #~ msgstr "Bleeh"

* Previous msgid

  .. code-block:: po

    #| msgid "previous message"

* Previous msgctxt

  .. code-block:: po

    #| msgctxt "previous context"


