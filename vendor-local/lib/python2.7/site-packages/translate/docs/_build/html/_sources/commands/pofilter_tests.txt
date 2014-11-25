
.. _pofilter_tests:

.. _descriptions_of_all_pofilter_tests:

Descriptions of all pofilter tests
**********************************

The following are descriptions of the tests available in :doc:`pofilter`,
:ref:`Pootle <pootle:checks>` and :ref:`Virtaal <virtaal:checks>` with some
details about what type of errors they are useful to test for and the
limitations of each test.

Keep in mind that the software might point to errors which are not necessarily
wrong (false positives).

Currently there are 47 tests.  You can always get a list of the currently
available tests by running::

  pofilter -l

To see test specific to a specific targetted application or group of
applications run::

  pofilter --gnome -l

.. _adding_new_tests_and_new_language_adaptations:

Adding new tests and new language adaptations
=============================================

If you have an idea for a new test or want to add target language adaptations
for your language then please help us with information about your test idea and
the specifics of your language.

.. _test_classification:

Test Classification
===================

Some tests are more important than others so we have classified them to help
you determine which to run first.

* Critical -- can break a program

  * :ref:`pofilter_tests#escapes`,
    :ref:`pofilter_tests#newlines`, :ref:`pofilter_tests#nplurals`,
    :ref:`pofilter_tests#printf`, :ref:`pofilter_tests#tabs`,
    :ref:`pofilter_tests#variables`, :ref:`pofilter_tests#xmltags`,
    :ref:`pofilter_tests#dialogsizes`

* Functional -- may confuse the user

  * :ref:`pofilter_tests#accelerators`,
    :ref:`pofilter_tests#acronyms`, :ref:`pofilter_tests#blank`,
    :ref:`pofilter_tests#emails`, :ref:`pofilter_tests#filepaths`,
    :ref:`pofilter_tests#functions`, :ref:`pofilter_tests#gconf`,
    :ref:`pofilter_tests#kdecomments`, :ref:`pofilter_tests#long`,
    :ref:`pofilter_tests#musttranslatewords`,
    :ref:`pofilter_tests#notranslatewords`, :ref:`pofilter_tests#numbers`,
    :ref:`pofilter_tests#options`, :ref:`pofilter_tests#purepunc`,
    :ref:`pofilter_tests#sentencecount`, :ref:`pofilter_tests#short`,
    :ref:`pofilter_tests#spellcheck`, :ref:`pofilter_tests#urls`,
    :ref:`pofilter_tests#unchanged`

* Cosmetic -- make it look better

  * :ref:`pofilter_tests#brackets`, :ref:`pofilter_tests#doublequoting`,
    :ref:`pofilter_tests#doublespacing`, :ref:`pofilter_tests#doublewords`,
    :ref:`pofilter_tests#endpunc`, :ref:`pofilter_tests#endwhitespace`,
    :ref:`pofilter_tests#puncspacing`, :ref:`pofilter_tests#simplecaps`,
    :ref:`pofilter_tests#simpleplurals`, :ref:`pofilter_tests#startcaps`,
    :ref:`pofilter_tests#singlequoting`, :ref:`pofilter_tests#startpunc`,
    :ref:`pofilter_tests#startwhitespace`, :ref:`pofilter_tests#validchars`

* Extraction -- useful mainly for extracting certain types of string

  * :ref:`pofilter_tests#compendiumconflicts`, :ref:`pofilter_tests#credits`,
    :ref:`pofilter_tests#hassuggestion`, :ref:`pofilter_tests#isfuzzy`,
    :ref:`pofilter_tests#isreview`, :ref:`pofilter_tests#untranslated`

.. _test_description:

Test Description
================

.. _pofilter_tests#accelerators:

accelerators
------------

Checks whether :ref:`accelerators <guide:accelerators>` are consistent between
the two strings.

Make sure you use the :opt:`--mozilla`, :opt:`--kde`, etc options so that
pofilter knows which type of accelerator it is looking for.  The test will pick
up accelerators that are missing and ones that shouldn't be there.

.. _pofilter_tests#acronyms:

acronyms
--------

Checks that acronyms that appear are unchanged.

If an acronym appears in the original this test will check that it appears in
the translation.  Translating acronyms is a language decision but many
languages leave them unchanged. In that case this test is useful for tracking
down translations of the acronym and correcting them.

.. _pofilter_tests#blank:

blank
-----

Checks whether a translation is totally blank.

This will check to see if a translation has inadvertently been translated as
blank i.e. as spaces.  This is different from untranslated which is completely
empty.  This test is useful in that if something is translated as "   " it will
appear to most tools as if it is translated.

.. _pofilter_tests#brackets:

brackets
--------

Checks that the number of brackets in both strings match.

If ``([{`` or ``}])`` appear in the original this will check that the same
number appear in the translation.

.. _pofilter_tests#compendiumconflicts:

compendiumconflicts
-------------------

Checks for Gettext compendium conflicts (``#-#-#-#-#``).

When you use msgcat to create a PO compendium it will insert ``#-#-#-#-#`` into
entries that are not consistent.  If the compendium is used later in a message
merge then these conflicts will appear in your translations.  This test quickly
extracts those for correction.

.. _pofilter_tests#credits:

credits
-------

Checks for messages containing translation credits instead of normal.
translations.

Some projects have consistent ways of giving credit to translators by having a
unit or two where translators can fill in their name and possibly their contact
details. This test allows you to find these units easily to check that they are
completed correctly and also disables other tests that might incorrectly get
triggered for these units (such as urls, emails, etc.)

.. _pofilter_tests#dialogsizes:

dialogsizes
-----------

Checks that dialog sizes are not translated.

This is a Mozilla specific test.  Mozilla uses a language called XUL to define
dialogues and screens.  This can make use of CSS to specify properties of the
dialogue.  These properties include things such as the width and height of the
box.  The size might need to be changed if the dialogue size changes due to
longer translations. Thus translators can change these settings.  But you are
only meant to change the number not translate the words 'width' or 'height'.
This check capture instances where these are translated.  It will also catch
other types of errors in these units.

.. _pofilter_tests#doublequoting:

doublequoting
-------------

Checks whether doublequoting is consistent between the two strings.

Checks on double quotes ``"`` to ensure that you have the same number in both
the original and the translated string. This tests takes into account that
several languages use different quoting characters, and will test for them
instead.

.. _pofilter_tests#doublespacing:

doublespacing
-------------

Checks for bad double-spaces by comparing to original.

This will identify if you have [space][space] in when you don't have it in the
original or it appears in the original but not in your translation. Some of
these are spurious and how you correct them depends on the conventions of your
language.

.. _pofilter_tests#doublewords:

doublewords
-----------

Checks for repeated words in the translation.

Words that have been repeated in a translation will be highlighted with this
test e.g. "the the", "a a".  These are generally typos that need correcting.
Some languages may have valid repeated words in their structure, in that case
either ignore those instances or switch this test off using the
:opt:`--excludefilters` option.

.. _pofilter_tests#emails:

emails
------

Checks to see that emails are not translated.

Generally you should not be translating email addresses.  This check will look
to see that email addresses e.g. info@example.com are not translated.  In some
cases of course you should translate the address but generally you shouldn't.

.. _pofilter_tests#endpunc:

endpunc
-------

Checks whether punctuation at the end of the strings match.

This will ensure that the ending of your translation has the same punctuation
as the original.  E.g. if it ends in :[space] then so should yours.  It is
useful for ensuring that you have ellipses [...] in all your translations, not
simply three separate full-stops. You may pick up some errors in the original:
feel free to keep your translation and notify the programmers.  In some
languages, characters such as ? ! are always preceded by a space e.g. [space]?
— do what your language customs dictate. Other false positives you will notice
are, for example, if through changes in word-order you add "), etc. at the end
of the sentence. Do not change these: your language word-order takes
precedence.

It must be noted that if you are tempted to leave out [full-stop] or [colon] or
add [full-stop] to a sentence, that often these have been done for a reason,
e.g. a list where fullstops make it look cluttered.  So, initially match them
with the English, and make changes once the program is being used.

This check is aware of several language conventions for punctuation characters,
such as the custom question marks for Greek and Arabic, Devenagari Danda,
full-width punctuation for CJK languages, etc.  Support for your language can
be added easily if it is not there yet.

.. _pofilter_tests#endwhitespace:

endwhitespace
-------------

Checks whether whitespace at the end of the strings matches.

Operates the same as endpunc but is only concerned with whitespace. This filter
is particularly useful for those strings which will evidently be followed by
another string in the program, e.g. [Password: ] or [Enter your username: ].
The whitespace is an inherent part of the string. This filter makes sure you
don't miss those important but otherwise invisible spaces!

If your language uses full-width punctuation (like Chinese), the visual spacing
in the character might be enough without an added extra space.

.. _pofilter_tests#escapes:

escapes
-------

Checks whether escaping is consistent between the two strings.

Checks escapes such as ``\n`` ``\uNNNN`` to ensure that if they exist in the.
original that you have them in the translation.

.. _pofilter_tests#filepaths:

filepaths
---------

Checks that file paths have not been translated.

Checks that paths such as ``/home/user1`` have not been translated.  Generally
you do not translate a file-path, unless it is being used as an example, e.g.
[your_user_name/path/to/filename.conf].

.. _pofilter_tests#functions:

functions
---------

Checks to see that function names are not translated.

Checks that function names e.g. ``rgb()`` or ``getEntity.Name()`` are not
translated.

.. _pofilter_tests#gconf:

gconf
-----

Checks if we have any gconf config settings translated.

Gconf settings should not be translated so this check checks that gconf
settings such as "name" or "modification_date" are not translated in the
translation.  It allows you to change the surrounding quotes but will ensure
that the setting values remain untranslated.

.. _pofilter_tests#hassuggestion:

hassuggestion
-------------

Checks if there is at least one suggested translation for this unit.

If a message has a suggestion (an alternate translation stored in alt-trans
units in XLIFF and .pending files in PO) then these will be extracted.  This is
used by Pootle and is probably only useful in pofilter when using XLIFF files.

.. _pofilter_tests#isfuzzy:

isfuzzy
-------

Checks if the po element has been marked fuzzy.

If a message is marked fuzzy in the PO file then it is extracted.  Note this is
different from :opt:`--fuzzy` and :opt:`--nofuzzy` options which specify
whether tests should be performed against messages marked fuzzy.

.. _pofilter_tests#isreview:

isreview
--------

Checks if the po element has been marked for review.

If you have made use of the 'review' flags in your translations::

  # (review) reason for review
  # (pofilter) testname: explanation for translator

Then if a message is marked for review in the PO file it will be extracted.
Note this is different from :opt:`--review` and :opt:`--noreview` options which
specify whether tests should be performed against messages already marked as
under review.

.. _pofilter_tests#kdecomments:

kdecomments
-----------

Checks to ensure that no KDE style comments appear in the translation.

KDE style translator comments appear in PO files as ``"_: comment\n"``. New
translators often translate the comment.  This test tries to identify instances
where the comment has been translated.

.. _pofilter_tests#long:

long
----

Checks whether a translation is much longer than the original string.

This is most useful in the special case where the translation is multiple
characters long while the source text is only 1 character long.  Otherwise, we
use a general ratio that will catch very big differences but is set
conservatively to limit the number of false positives.

.. _pofilter_tests#musttranslatewords:

musttranslatewords
------------------

Checks that words configured as definitely translatable don't appear in the
translation.

If for instance in your language you decide that you must translate 'OK' then
this test will flag any occurances of 'OK' in the translation if it appeared in
the source string.  You must specify a file containing all of the *must
translate* words using :opt:`--musttranslatefile`.

.. _pofilter_tests#newlines:

newlines
--------

Checks whether newlines are consistent between the two strings.

Counts the number of ``\n`` newlines (and variants such as ``\r\n``) and
reports and error if they differ.

.. _pofilter_tests#nplurals:

nplurals
--------

Checks for the correct number of noun forms for plural translations.

This uses the plural information in the language module of the toolkit.  This
is the same as the Gettext nplural value.  It will check that the number of
plurals required is the same as the number supplied in your translation.

.. _pofilter_tests#notranslatewords:

notranslatewords
----------------

Checks that words configured as untranslatable appear in the translation too.

Many brand names should not be translated, this test allows you to easily make
sure that words like: Word, Excel, Impress, Calc, etc. are not translated.  You
must specify a file containing all of the *no translate* words using
:opt:`--notranslatefile`.

.. _pofilter_tests#numbers:

numbers
-------

Checks whether numbers of various forms are consistent between the two strings.

You will see some errors where you have either written the number in full or
converted it to the digit in your translation.  Also changes in order will
trigger this error.

.. _pofilter_tests#options:

options
-------

Checks that command line options are not translated.

In messages that contain command line options, such as :opt:`--help`, this test
will check that these remain untranslated.  These could be translated in the
future if programs can create a mechanism to allow this, but currently they are
not translated.  If the options has a parameter, e.g. :opt:`--file=FILE`, then
the test will check that the parameter has been translated.

.. _pofilter_tests#printf:

printf
------

Checks whether printf format strings match.

If the printf formatting variables are not identical, then this will indicate
an error.  Printf statements are used by programs to format output in a human
readable form (they are place holders for variable data).  They allow you to
specify lengths of string variables, string padding, number padding, precision,
etc. Generally they will look like this: ``%d``, ``%5.2f``, ``%100s``, etc. The
test can also manage variables-reordering using the ``%1$s`` syntax.  The
variables' type and details following data are tested to ensure that they are
strictly identical, but they may be reordered.

.. seealso:: :wp:`printf Format String <Printf_format_string>`

.. _pofilter_tests#puncspacing:

puncspacing
-----------

Checks for bad spacing after punctuation.

In the case of [full-stop][space] in the original, this test checks that your
translation does not remove the space.  It checks also for [comma], [colon],
etc.

Some languages don't use spaces after common punctuation marks, especially
where full-width punctuation marks are used. This check will take that into
account.

.. _pofilter_tests#purepunc:

purepunc
--------

Checks that strings that are purely punctuation are not changed.

This extracts strings like "+" or "-" as these usually should not be changed.

.. _pofilter_tests#sentencecount:

sentencecount
-------------

Checks that the number of sentences in both strings match.

Adds the number of sentences to see that the sentence count is the same between
the original and translated string. You may not always want to use this test,
if you find you often need to reformat your translation, because the original
is badly-expressed, or because the structure of your language works better that
way. Do what works best for your language: it's the meaning of the original you
want to convey, not the exact way it was written in the English.

.. _pofilter_tests#short:

short
-----

Checks whether a translation is much shorter than the original string.

This is most useful in the special case where the translation is 1 characters
long while the source text is multiple characters long.  Otherwise, we use a
general ratio that will catch very big differences but is set conservatively to
limit the number of false positives.

.. _pofilter_tests#simplecaps:

simplecaps
----------

Checks the capitalisation of two strings isn't wildly different.

This will pick up many false positives, so don't be a slave to it.  It is
useful for identifying translations that don't start with a capital letter
(upper-case letter) when they should, or those that do when they shouldn't.  It
will also highlight sentences that have extra capitals; depending on the
capitalisation convention of your language, you might want to change these to
Title Case, or change them all to normal sentence case.

.. _pofilter_tests#simpleplurals:

simpleplurals
-------------

Checks for English style plural(s) for you to review.

This test will extract any message that contains words with a final "(s)" in
the source text.  You can then inspect the message, to check that the correct
plural form has been used for your language.  In some languages, plurals are
made by adding text at the beginning of words, making the English style messy.
In this case, they often revert to the plural form.  This test allows an editor
to check that the plurals used are correct.  Be aware that this test may create
a number of false positives.

For languages with no plural forms (only one noun form) this test will simply
test that nothing like "(s)" was used in the translation.

.. _pofilter_tests#singlequoting:

singlequoting
-------------

Checks whether singlequoting is consistent between the two strings.

The same as doublequoting but checks for the ``'`` character.  Because this is
used in contractions like it's and in possessive forms like user's, this test
can output spurious errors if your language doesn't use such forms.  If a quote
appears at the end of a sentence in the translation, i.e. ``'.``, this might
not be detected properly by the check.

.. _pofilter_tests#spellcheck:

spellcheck
----------

Checks for words that don't pass a spell-check.

This test will check for misspelled words in your translation.  The test first
checks for misspelled words in the original (usually English) text, and adds
those to an exclusion list. The advantage of this exclusion is that many words
that are specific to the application will not raise errors e.g. program names,
brand names, function names.

The checker works with `PyEnchant <http://pythonhosted.org/pyenchant/>`_. You
need to have PyEnchant installed as well as a dictionary for your language (for
example, one of the `Hunspell <https://wiki.openoffice.org/wiki/Dictionaries>`_
or `aspell <http://ftp.gnu.org/gnu/aspell/dict/>`_ dictionaries).  This test
will only work if you have specified the :opt:`--language` option.

The pofilter error that is created, lists the misspelled word, plus
suggestions returned from the spell checker.  That makes it easy for you to
identify the word and select a replacement.

.. _pofilter_tests#startcaps:

startcaps
---------

Checks that the message starts with the correct capitalisation.

After stripping whitespace and common punctuation characters, it then checks to
see that the first remaining character is correctly capitalised.  So, if the
sentence starts with an upper-case letter, and the translation does not, an
error is produced.

This check is entirely disabled for many languages that don't make a
distinction between upper and lower case. Contact us if this is not yet
disabled for your language.

.. _pofilter_tests#startpunc:

startpunc
---------

Checks whether punctuation at the beginning of the strings match.

Operates as endpunc but you will probably see fewer errors.

.. _pofilter_tests#startwhitespace:

startwhitespace
---------------

Checks whether whitespace at the beginning of the strings matches.

As in endwhitespace but you will see fewer errors.

.. _pofilter_tests#tabs:

tabs
----

Checks whether tabs are consistent between the two strings.

Counts the number of ``\t`` tab markers and reports an error if they differ.

.. _pofilter_tests#unchanged:

unchanged
---------

Checks whether a translation is basically identical to the original string.

This checks to see if the translation isn't just a copy of the English
original.  Sometimes, this is what you want, but other times you will detect
words that should have been translated.

.. _pofilter_tests#untranslated:

untranslated
------------

Checks whether a string has been translated at all.

This check is really only useful if you want to extract untranslated strings so
that they can be translated independently of the main work.

.. _pofilter_tests#urls:

urls
----

Checks to see that URLs are not translated.

This checks only basic URLs (http, ftp, mailto etc.) not all URIs (e.g. afp,
smb, file).  Generally, you don't want to translate URLs, unless they are
example URLs (http://your_server.com/filename.html).  If the URL is for
configuration information, then you need to query the developers about placing
configuration information in PO files.  It shouldn't really be there, unless it
is very clearly marked: such information should go into a configuration file.

.. _pofilter_tests#validchars:

validchars
----------

Checks that only characters specified as valid appear in the translation.

Often during character conversion to and from UTF-8 you get some strange
characters appearing in your translation.  This test presents a simple way to
try and identify such errors.

This test will only run of you specify the :opt:`--validcharsfile` command line
option.  This file contains all the characters that are valid in your language.
You must use UTF-8 encoding for the characters in the file.

If the test finds any characters not in your valid characters file then the
test will print the character together with its Unicode value (e.g. 002B).

.. _pofilter_tests#variables:

variables
---------

Checks whether variables of various forms are consistent between the two strings.

This checks to make sure that variables that appear in the original also appear
in the translation.  Make sure you use the :opt:`--kde`, :opt:`--openoffice`,
etc flags as these define what variables will be searched for.  It does not at
the moment cope with variables that use the reordering syntax of Gettext PO
files.

.. _pofilter_tests#xmltags:

xmltags
-------

Checks that :wiki:`XML/HTML <guide/translation/html>` tags have not been
translated.

This check finds the number of tags in the source string and checks that the
same number are in the translation.  If the counts don't match then either the
tag is missing or it was mistakenly translated by the translator, both of which
are errors.

The check ignores tags or things that look like tags that cover the whole
string e.g. "<Error>" but will produce false positives for things like "An
<Error> occurred" as here "Error" should be translated.  It also will allow
translation of the alt attribute in e.g. <img src=bob.png alt="Image
description"> or similar translatable attributes in OpenOffice.org help files.
