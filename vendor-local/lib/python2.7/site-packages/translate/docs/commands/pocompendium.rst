
.. _pocompendium:

pocompendium
************

Takes a directory of translated PO files and creates a single PO files called a
PO compendium.  This compendium can be used to review word choice conflicts or
as input during a merge using :doc:`pomigrate2`.

.. _pocompendium#prerequisites:

Prerequisites
=============

GNU Gettext:

* :man:`msgattrib`
* :man:`msgcat`
* :man:`msghack` (may not be present on your installation of Gettext, but is
  only required for the invert command)
* :man:`msgfilter`

.. _pocompendium#usage:

Usage
=====

::

  pocompendium [options] output.po <-d po-directory(ies)|po-file(s)>

Where:

+--------------------+-------------------------------------------------------------+
| output.po          | the name of the output PO compendium                        |
+--------------------+-------------------------------------------------------------+
| po-directory(ies)  | one or more directories to use as input for the compendium  |
+--------------------+-------------------------------------------------------------+
| po-file(s)         | one or more PO files to use as input for the compendium     |
+--------------------+-------------------------------------------------------------+

Options:

-v, --invert    swap the msgid and msgstr in the input PO files
-e, --errors    only return those msg blocks that have conflicts
-i, --ignore-case    drops all msgstr's to lowercase
-st, -tilde, --strip-accel-amp   remove all & style accelerator markers
-sa, -amp, --strip-accel-tilde   remove all ~ style accelerator markers
-su, --strip-accel-under         remove all _ style accelerator markers

.. _pocompendium#examples:

Examples
========

- *Compendium creation* --- create a compendium with all your translations to
  use as input during a message merge either when migrating an existing project
  or starting a new one.
- *Conflicting translations* --- use :opt:`--errors` to find where you have
  translated an English string differently.  Many times this is OK but often it
  will pick up subtle spelling mistakes or help you to migrate older
  translations to a newer choice of words
- *Conflicting word choice* --- use :opt:`--invert` and :opt:`--errors` to get
  a compendium file that show how you have used a translated word for different
  English words. You might have chosen a word that is valid for both of the
  English expressions but that in the context of computers would cause
  confusion for the user.  You can now easily identify these words and make
  changes in the underlying translations.

.. _pocompendium#narrowing_results:

Narrowing Results
=================

PO files treat slight changes in capitalisation, accelerator, punctuation and
whitespace as different translations.  In cases 2) and 3) above it is sometimes
useful to remove the inconsistencies so that you can focus on the errors in
translation not on shifts in capitals.  To this end you can use the following:

:opt:`--ignore-case`, :opt:`--strip-accel-amp`, :opt:`--strip-accel-tilde`,
:opt:`--strip-accel-under`

.. _pocompendium#operation:

Operation
=========

pocompendium makes use of the Gettext tool msgcat to perform its task.  It
traverses the PO directories and cat's all found PO files into the single
compendium output file.  It then uses msgattrib to extract only certain
messages, msghack to invert messages and msgfilter to convert messages to
lowercase.

.. _pocompendium#bugs:

Bugs
====

There are some absolute/relative path name issues
