
.. _podebug:

podebug
*******

Insert :wp:`pseudo translations <Pseudolocalization>` or debug markers into
target text in XLIFF, Gettex PO and other localization files.

The pseudo translation or debug markers make it easy to reference and locate
strings when your translated application is running.

Use it to:

* *Target your translations*: see what files are being referenced for string
  appearing in your programs.
* *Debug translations*: if you know in what file the message occurs then you
  can quickly find it and fix it.
* *Check that everything is translatable*: any English only text needs to be
  analysed so that it can be localised.
* *Check for Unicode compliance*: by inserting Unicode text outside of the
  Latin range it allows you to check that your program can handle non-Latin
  correctly.

.. _podebug#usage:

Usage
=====

::

  podebug [options] <in> <out>

Where:

+-------+----------------------------------------------------------------+
| <in>  | is an input directory or localisation file file                |
+-------+----------------------------------------------------------------+
| <out> | is an output directory or localisation file, if missing output |
|       | will be to standard out.                                       |
+-------+----------------------------------------------------------------+

Options:

--version              show program's version number and exit
-h, --help             show this help message and exit
--manpage              output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names,
                       verbose <option_progress>`
--errorlevel=ERRORLEVEL
                       show errorlevel as: :doc:`none, message, exception,
                       traceback <option_errorlevel>`
-iINPUT, --input=INPUT  read from INPUT in po, pot formats
-xEXCLUDE, --exclude=EXCLUDE
                       exclude names matching EXCLUDE from input paths
-oOUTPUT, --output=OUTPUT
                       write to OUTPUT in po, pot formats
-P, --pot              output PO Templates (.pot) rather than PO files (.po)
-fFORMAT, --format=FORMAT     specify format string
--rewrite=STYLE        the translation rewrite style: :doc:`xxx, en, blank,
                       chef  (v1.2), unicode (v1.2) <option_rewrite>`
--ignore=APPLICATION   apply tagging ignore rules for the given application:
                       kde, gtk, openoffice, libreoffice, mozilla
--hash=LENGTH          add an md5 hash to translations (only until version
                       1.3.0 -- see %h below)

.. _podebug#formats:

Formats
=======

A format string can have these various options:

+---+----------------------------------------------------+
| f | full filename including directory                  |
+---+----------------------------------------------------+
| F | as %f but with .po file extension                  |
+---+----------------------------------------------------+
| b | base of filename                                   |
+---+----------------------------------------------------+
| B | base of filename with .po file extension           |
+---+----------------------------------------------------+
| d | directory name                                     |
+---+----------------------------------------------------+
| s | preset OpenOffice.org modifier                     |
+---+----------------------------------------------------+
| c | use only consonants                                |
+---+----------------------------------------------------+
| h | hash value (since version 1.4 -- see notes below)  |
+---+----------------------------------------------------+
| N | a set number of characters                         |
+---+----------------------------------------------------+

A format string may look like this:

* ``%cf`` -- the full filename without vowels
* ``[%10cb] `` -- the first ten character after compressing the base of the
  filename and place it in square brackets with a space before the real message
* ``[%5cd - %cB] `` -- the first 5 consonants of the directory, followed by a
  dash then the consonants of the filename with a .po extension.  All
  surrounded by square brackets with a space before the translations.
* ``%4h.`` -- insert a hash value of length 4

Complex format strings may make it too difficult to actually read the
translation, so you are probably best served using as short a string as
possible.

.. _podebug#rewriting_style:

Rewriting (style)
=================

The rewriting options are designed to change the target text in various ways
(c.f. the various :doc:`rewriting styles <option_rewrite>` available).  This is
mostly valuable for debugging English text.  The 'xxx' rewriter is useful in
that it allows you to identify text that has not localisable as that text will
lack the xxx characters.

The 'en' rewriter can be used to prepare English hashed (see below) files for
quickly finding strings that have spelling or other errors.  It can also be
used to create a translated English file which can then be used for other
purposes such as British English translation.

.. _podebug#ignoring_messages:

Ignoring messages
=================

In some applications their are translations that should not be translated
(usually these are configuration options).  If you do translate them then the
application will fail to compile or run.

The :opt:`--ignore` option allows you to specify the application for which you
are producing PO debug files.  In this case it will then not mark certain of
the PO entries with debug messages.

In Mozilla we do not mark lone ``.accesskey``, ``.width``, ``.height``, etc
since these can really be thought of as configuration options.

.. _podebug#hashing:

Hashing
=======

Sometimes you find an error in a string.  But it is difficult to search for the
occurance of the error.  In order to make it easy to find a string in your
files we can produce a hash on the strings location and other data.  This
produces unique alphanumeric sequences which are prepended to the target text.
Thus now in your application you have your translated text and a alphanumeric
value.  Its is then easy to search for that value and find your problem string.

.. _podebug#more_reading:

Usings podebug
==============

Here are some more examples in a `series
<http://translate.org.za/blogs/friedel/en/content/pseudolocalisation-podebug-1>`_
`of
<http://translate.org.za/blogs/friedel/en/content/pseudolocalisation-podebug-2>`_
`blog posts
<http://translate.org.za/blogs/friedel/en/content/pseudolocalisation-podebug-3-interview-rail-aliev>`_.
