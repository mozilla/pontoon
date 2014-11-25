
.. _migrating_translations:

Migrating your translations
***************************

You very often need to migrate older translations to newer template or POT
files.  There are a number of Gettext tools that can manage this but they do
not handle the situation where files have been renamed and moved.  The
:doc:`/commands/pomigrate2` script allows us to migrate between versions where
there has been considerable change.

This migration HOWTO takes you through the steps in a generic fashion so that
you can apply it to any of your projects.  We use OpenOffice.org as an example
for clarity.  Our task in the examples is to migrate old translation for
OpenOffice.org 1.1.3 to OpenOffice.org 2.0.

.. _migrating_translations#requirements:

Requirements
============

You will need:

* :doc:`/commands/pomigrate2`
* :doc:`/commands/pocompendium`
* A text editor
* A PO editing tool

.. _migrating_translations#preparing_the_new_pot_files:

Preparing the new POT files
===========================

We need the new POT files.  Either download these from the project or generate
them using :doc:`/commands/moz2po`, :doc:`/commands/oo2po` or the other tools
of the Translate Toolkit.  The POT files are templates for the destination
files that we will be creating.

::

  oo2po -P en-US.sdf ooo-20-pot

This will create new POT files in *ooo-20-pot*.

.. _migrating_translations#checking_your_old_po_files_for_errors:

Checking your old PO files for errors
=====================================

We will be migrating your old PO files into the new POT files.  This is a good
opportunity to check for encoding errors and inconsistencies.

We use :doc:`/commands/pocompendium` to check for encoding errors::

  pocompendium check.po -d ooo-113-old

This will create a compendium PO files, *check.po*, from all the PO files in
the directory *ooo-113-old*, where *ooo-113-old* contains all your old
translations.  pocompendium is a wrapper around various Gettext tools, encoding
errors will appear as errors from those tools.

Use your text editor to find and correct these errors.  If you do not correct
these now they will migrate to your new version.  Once encoding errors are
fixed they're usually gone for good, so it is time well spent.

.. _migrating_translations#optional:_checking_your_old_po_files_for_consistency:

Optional: Checking your old PO files for consistency
====================================================

.. note:: Note this step is optional, a more detailed explanation is given in
   :doc:`checking_for_inconsistencies`.

We now look at consistency within the translations.  The first check extracts
situations were the same English string was translated in two different ways::

  pocompendium --ignore-case --accel-amp --errors check.po -d ooo-113-old

In *check.po* you will find all situations where the same English text was
translated differently.  We use :opt:`--accel-amp` to remove accelerator
markers (you'll change this depending on the one used by the project -- we can
do & _ or ~).   Now view *check.po* in a PO editor or text editor.  You will
need to correct each inconsistency in the source PO files, using *check.po* as
the guide.  Many of the errors are usually spelling mistakes.  You can
regenerate *check.po* from time to time until all inconsistencies are justified
or removed.

Then we check for words in your language that are used for more than one
English concept.  You don't for instance want the same word for *Cancel* and
*Delete*.  For this we invert the compendium::

  pocompendium --invert --ignore-case --accel-amp --errors check.po -d ooo-113-old

We now have a file similar to the previous one except your language appears in
the msgid and the English appears in the msgstr.  Look for inconsistencies that
would cause problems for the user and correct them in the source files.

.. _migrating_translations#migrate:

Migrate
=======

You are now ready to migrate using :doc:`/commands/pomigrate2`.  You have
created your destination POT files and all your PO files are clean and ready to
migrate.

::

  pomigrate2 ooo-113-old ooo-20-new ooo-20-pot

This will take all translations from *ooo-113-old* and migrate them to
*ooo-20-new* using *ooo-20-pot* as templates.  By default pomigrate2 migrates
without any fancy text matching, there are options to allow for fuzzy matching
and the use of a compendium.  Read the :doc:`/commands/pomigrate2` help page to
find out more about these options.

.. _migrating_translations#techie:_what_does_pomigrate2_do_to_your_file:

Techie: what does pomigrate2 do to your file?
---------------------------------------------

This section is for those insanely curious about what pomigrate will do to
their files. You don't need to understand this section :-)

* Init stage

  * If a file has not changed location between old and new then it is simply
    copied across
  * If it has moved then we try to find a file by the same name and move ours
    there.  If there are multiple files by the same name, then we join them
    together and copy them
  * If a file does not exist then we initialise it

* Update stage

  * We now update our translations using msgmerge or pot2po
  * If you asked for a compendium, we will build one from the existing files
    and update using it and optionally other external compendiums

That's it. At the end you should have every file that needs translation updated
to the latest template files.  Files that moved should still be preserved and
not lost.  Files that where renamed will still be translated if you used a
compendium otherwise they will be untranslated.

.. _migrating_translations#how_well_did_you_do:

How well did you do
===================

Congratulations! Your files are now migrated.

You might want to see how much of your old work was reusable in the new
version::

  pocount ooo-20-new

This will use :doc:`/commands/pocount` to count the words in your new files and
you can compare the number of translate and untranslated messages from your old
version.

.. _migrating_translations#conclusion:

Conclusion
==========

Your files have now been migrated and are ready for updating.  If files have
been moved or renamed, and you used a compendium, then most likely you have
most of that work translated.
