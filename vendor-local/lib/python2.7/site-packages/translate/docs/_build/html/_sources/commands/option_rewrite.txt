
.. _option_rewrite:

--rewrite=STYLE
***************

:doc:`podebug` allows you to rewrite the output text in a number of ways.

.. _option_rewrite#xxx:

xxx
===

The target text is surrounded by ``xxx`` as follows

.. code-block:: po

  msgid "English"
  msgstr "xxxEnglishxxx"

This is useful when you want to identify which text is localisable.  There
might be text in your application which you cannot localise this will allow you
to quickly identify that text.

.. _option_rewrite#en:

en
==

The source text is copied to the target

.. code-block:: po

  msgid "English"
  msgstr "English"

In this way you can create translations that contain only the source text.
Useful if you are preparing a roundtrip test or want to start an English
derived translation such as British English.  It produces the same results as
:man:`msgen` but with the advantage that you can add debug markers.

.. _option_rewrite#blank:

blank
=====

This simply empties your current translations

.. code-block:: po

  msgid "English"
  msgstr ""

When you have a set of translation files but no template this allows you to
essentially convert a PO into a POT file.  This mimics the :opt:`--empty`
functionality of :man:`msghack`.

.. _option_rewrite#bracket:

bracket
=======

.. versionadded:: 1.4

Places brackets around the translated text.

.. code-block:: po

  msgid "English"
  msgstr "[English]"

This can be used in the same way as ``xxx`` to check for translatability.  It
is also useful with very long strings as it allows you to check that the full
string in rendered and has not been cutoff by the application.

.. _option_rewrite#chef:

chef
====

.. versionadded:: 1.2

Rewrites the source text using mock Swedish as popularised by the :wp:`Swedish
Chef <Swedish_Chef>`.

.. code-block:: po

  msgid "English"
  msgstr "Ingleesh"

This is probably only useful for some fun.  It's not guaranteed that every
string will be rewritten as the mock Swedish rules might not apply thus its not
ideal for identifying untranslatable strings.

.. _option_rewrite#flipped:

flipped
=======

.. versionadded:: 1.4

Change the text into a version that uses equivalent Latin characters that are
upside down.

.. code-block:: po

  msgid "English"
  msgstr "‮Ǝuƃʅısɥ"

``flipped`` can give an output that simulates RTL languages.  It inserts RTL
characters to try to achieve RTL-like results.  Its not perfect but will give
you some sense of whether your application can do RTL.  Or just use it for fun!

For really testing right-to-left GUIs, you want to make sure that the whole
application is shown in RTL, not just the strings. Test your pseudo-translated
file as a translation of an RTL language like Arabic or Hebrew. In case the
application relies on other files coming from libraries (like GTK+), you might
need to repeat the process for them, or at least ensure that you have the
Arabic/Hebrew .mo files for them installed.

.. _option_rewrite#unicode:

unicode
=======

.. versionadded:: 1.2

Rewrites the source text with Unicode characters that looks like the Latin
characters that they are replacing.

.. code-block:: po

  msgid "English"
  msgstr "Ḗƞɠŀīşħ"

This allows a translator or programmer to test a programs ability to use
Unicode message strings. By using characters in the Unicode range but that are
related to the plain Latin characters that they replace we ensure that the
messages are still readable.

.. note:: Before version 1.4, the rewrite rule will also rewrite variables
   and XML tags, which would cause problems in some situations.
   Run :doc:`pofilter` as a quick method to fix up incorrect changes, or
   upgrade to version 1.4.

