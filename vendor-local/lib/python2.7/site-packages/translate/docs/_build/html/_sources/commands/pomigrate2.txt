
.. _pomigrate2:

pomigrate2
**********

pomigrate2 aims to move an existing translation to a new version based on
updated PO Template files automatically without user intervention.  Therefore
it is ideal for when you are migrating many languages or migrating from related
but divergent products e.g.  Mozilla to Firefox.

.. _pomigrate2#prerequisites:

Prerequisites
=============

GNU Gettext:

* :man:`msginit`
* :man:`msgcat`
* :man:`msgmerge`

.. _pomigrate2#usage:

Usage
=====

::

  pomigrate [options] <from> <to> <new templates>

Where:

+----------------+--------------------------------------------------------------+
| from           | is a directory of existing PO files                          |
+----------------+--------------------------------------------------------------+
| to             | is the directory where the migrated PO files will be stored  |
+----------------+--------------------------------------------------------------+
| new templates  | this is the directory that contains the PO Template files    |
+----------------+--------------------------------------------------------------+

Options:

-F, --use-fuzzy-matching
                 use fuzzy algorithms when merging to attempt to match strings
-C, --use-compendium
                 create and use a compendium built from the migrating files
-C, --use-compendium=COMPENDIUM
                 use an external compendium during the migration
--no-wrap        do not wrap long lines
--locale         set locale for newly born files
-q, --quiet      suppress most output
-p, --pot2po     use pot2po instead of msgmerge to migrate

.. _pomigrate2#operation:

Operation
=========

pomigrate2 makes use of the Gettext tools msgmerge or Translate Toolkit's
:doc:`pot2po` to perform its merging tasks.

It firstly finds all files with the same name and location in the <from>
directory as in the <template> directory and copies these to the <to>
directory.  If there is no file in the <from> directory to match one needed by
the <template> directory then it will msgcat all files in the <from> directory
with the same name and copy them to the correct destination in the <to>
directory.  If all of that fails then msginit is used to initialise any missing
PO files.

Lastly all the files in <to> are merged using msgmerge or pot2po.  This process
updates the files to match the layout and messages in <templates>.  Optionally,
by using :opt:`--use-compendium`, a compendium of all the translations in
<from> can be created to be used in the final merge process.
