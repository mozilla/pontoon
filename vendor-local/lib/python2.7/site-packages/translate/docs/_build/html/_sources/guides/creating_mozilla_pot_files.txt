
.. _creating_mozilla_pot_files:

Creating Mozilla POT files
**************************

You can do this using Mozilla source from CVS or Mercurial

.. _creating_mozilla_pot_files#using_mercurial:

Using Mercurial
===============

Since Firefox 3.1 and Thunderbird 3.0, Mozilla has switched to using Mercurial
for version control. See the Mozilla's `L10n on Mercurial
<https://developer.mozilla.org/docs/Localizing_with_Mercurial>`_ page for
instructions on how to checkout and update your Mozilla sources and l10n files.

You can use :ref:`get_moz_enUS.py <get_moz_enus.py>` to
extract an en-US directory from the source tree:

::

  get_moz_enUS.py -s mozilla-central/ -d l10n/ -p browser

This will move the correct en-US files to ``l10n/en-US``.  You can now create
POT files as follows::

  moz2po -P l10n/en-US l10n/pot

This will create the POT files in ``l10n/pot`` using the American English files
from ``en-US``.  You now have a set of POT files that you can use for
translation or updating your existing PO files.

There are also :doc:`other scripts </commands/mozilla_l10n_scripts>` that can
help with creating and updating POT and PO files for Mozilla localisation.

.. _creating_mozilla_pot_files#using_cvs:

Using CVS
=========

Firefox versions before 3.1 and Thunderbird versions before 3.0 still has its
source in CVS. Check out files from the Mozilla repository. If you don't want
to checkout all files do::

  make -f client.mk l10n-checkout

The English files are in the ``mozilla/`` module, while the translated files
all reside in the ``l10n/`` module.  They have different structure but not
enough to kill you.

Once you have checked out ``mozilla/`` you will need to get the correct files
for en-US.  To do this we will create en-US as a pseudo language.

::

  make -f tools/l10n/l10n.mk create-en-US

This will move the correct en-US files to ``l10n/en-US``.  You can now create
POT files as follows::

  moz2po -P l10n/en-US l10n/pot

This will create the POT files in ``l10n/pot`` using the American English files
from ``en-US``.  You now have a set of POT files that you can use for
translation or updating your existing PO files.
