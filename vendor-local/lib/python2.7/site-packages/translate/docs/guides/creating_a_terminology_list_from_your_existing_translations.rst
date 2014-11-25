
.. _creating_a_terminology_list_from_your_existing_translations:

Creating a terminology list from your existing translations
***********************************************************

If you did not create a terminology list when you started your translation
project or if you have inherited some old translations you probably now want to
create a terminology list.

A terminology list or glossary is a list of words and phrases with their
expected translation.  They are useful for ensuring that your translations are
consistent across your project.

With existing translations you have embedded a list of valid translation.  This
example will help you to extract the terms.  It is only the first step you will
need to review the terms and must not regard this as a complete list.  And of
course you would want to take your corrections and feed them back into the
original translations.

.. _creating_a_terminology_list_from_your_existing_translations#quick_overview:

Quick Overview
==============

This describes a multi-stage process for extracting terminology from
translation files.  It is provided for historical interest and completeness,
but you will probably find that using :doc:`/commands/poterminology` is easier
and will give better results than following this process.

- Filter our phrases of more than N words
- Remove obviously erroneous phrases such as numbers and punctuation
- Create a single PO compendium
- Extract and review items that are fuzzy and drop untranslated items
- Create a new PO files and process into CSV and TMX format

.. _creating_a_terminology_list_from_your_existing_translations#get_short_phrases_from_the_current_translations:

Get short phrases from the current translations
===============================================

We will not be able to identify terminology within bodies of text, we are only
going to extract short bit of text i.e. ones that are between 1 and 3 words
long.

::

  pogrep --header --search=msgid -e '^\w+(\s+\w+){0,2}$' zulu zulu-short

We use :opt:`--header` to ensure that the PO files have a header entry (which
is important for encoding).  We are searching only in the msgid and the regular
expression we use is looking for a string with between 1 and 3 words in it.  We
are searching through the folder *zulu* and outputting the result in
*zulu-short*

.. _creating_a_terminology_list_from_your_existing_translations#remove_any_translations_with_issues:

Remove any translations with issues
===================================

You can for instance remove all entries with only a single letter.  Useful for
eliminating all those spurious accelerator keys.

::

  pogrep --header --search=msgid -v -e "^.$" zulu-short zulu-short-clean

We use the :opt:`-v` option to invert the search.  Our *cleaner* potential
glossary words are now in *zulu-short-clean*.  What you can eliminate is only
limited by your ability to build regular expressions but yu could eliminate:

* Entries with only numbers
* Entries that only contain punctuation

.. _creating_a_terminology_list_from_your_existing_translations#create_a_compendium:

Create a compendium
===================

Now that we have our words we want to create a sinlge files of all terminology.
Thus we create a PO compendium::

  ~/path/to/pocompendium -i -su zulu-gnome-glossary.po -d zulu-short-clean

You can use various methods but our bash script is quite good.  Here we ignore
case, :opt:`-i`, and ignore the underscore (_) accelerator key, :opt:`-su`,
outputting the results in.

We now have a single file containing all glossary terms and the clean up and
review can begin.

.. _creating_a_terminology_list_from_your_existing_translations#split_the_file:

Split the file
==============

We want to split the file into translated, untranslated and fuzzy entries::

  ~/path/to/posplit ./zulu-gnome-glossary.po

This will create three files:

* zulu-gnome-glossary-translated.po -- all fully translated entries
* zulu-gnome-glossary-untranslated.po -- messages with no translation
* zulu-gnome-glossary-fuzzy.po -- words that need investigation

::

  rm zulu-gnome-glossary-untranslated.po

We discard ``zulu-gnome-glossary-untranslated.po`` since they are of no use to
us.

.. _creating_a_terminology_list_from_your_existing_translations#dealing_with_the_fuzzies:

Dealing with the fuzzies
========================

The fuzzies come in two kinds.  Those that are simply wrong or needed updating
and those where there was more then one translation for a given term.  So if
someone had translated 'File' differently across the translations we'd have an
entry that was marked fuzzy with the two options displayed.

::

  pofilter -t compendiumconflicts zulu-gnome-glossary-fuzzy.po zulu-gnome-glossary-conflicts.po

These compedium conflicts are what we are interested in so we use pofilter to
filter them from the other fuzzies.

::

  rm zulu-gnome-glossary-fuzzy.po

We discard the other fuzzies as they where probably wrong in the first place.
You could review these but it is not recommended.

Now edit ``zulu-gnome-glossary-conflicts.po`` to resolve the conflicts.  You
can edit them however you like but we usually follow the format::

  option1, option2, option3

You can get them into that layout by doing the following::

  sed '/#, fuzzy/d; /\"#-#-#-#-# /d; /# (pofilter) compendiumconflicts:/d; s/\\n"$/, "/' zulu-gnome-glossary-conflicts.po > tmp.po
  msgcat tmp.po > zulu-gnome-glossary-conflicts.po

Of course if a word is clearly wrong, misspelled etc. then you can eliminate
it.  Often you will find the "problem" relates to the part of speech of the
source word and that indeed there are two options depending on the context.

You now have a cleaned fuzzy file and we are ready to proceed.

.. _creating_a_terminology_list_from_your_existing_translations#put_it_back_together_again:

Put it back together again
==========================

::

  msgcat zulu-gnome-glossary-translated.po zulu-gnome-glossary-conflicts.po > zulu-gnome-glossary.po

We now have a single file ``zulu-gnome-glossary.po`` which contains our
glossary texts.

.. _creating_a_terminology_list_from_your_existing_translations#create_other_formats:

Create other formats
====================

It is probably good to make your terminology available in other formats.  You
can create CSV and TMX files from your PO.

::

  po2csv zulu-gnome-glossary.po zulu-gnome-glossary.csv
  po2tmx -l zu zulu-gnome-glossary.po zulu-gnome-glossary.tmx

For the terminology to be usable by Trados or Wordfast translators they need to
be in the following formats:

* Trados -- comma delimited file ``source,target``
* Wordfast -- tab delimited file ``source[tab]target``

In that format they are now available to almost all localisers in the world.

FIXME need scripts to generate these formats.

.. _creating_a_terminology_list_from_your_existing_translations#the_work_has_only_just_begun:

The work has only just begun
****************************

The lists you have just created are useful in their own right.  But you most
likely want to keep growing them, cleaning and improving them.

You should as a first step review what you have created and fix spelling and
other errors or disambiguate terms as needed.

But congratulations a Terminology list or Glossary is one of your most
important assets for creating good and consistent translations and it acts as a
valuable resource for both new and experienced translators when they need
prompting as to how to translate a term.
