
.. _mozilla_l10n_scripts:

Mozilla L10n Scripts
********************

.. _mozilla_l10n_scripts#introduction:

Introduction
============
This page describes the purpose and usage of scripts available in the Translate
Toolkit specifically for making the translation of Mozilla products easier.

Mozilla's move from CVS to Mercurial made a lot of these scripts necessary. For
more information about Mozilla l10n from CVS, see the :doc:`moz-l10n-builder`
page.

All of these scripts are available on Subversion from `here
<https://github.com/translate/translate/tree/master/tools/mozilla>`_.

We are currently generating POT files for most major betas, RCs and releases of
Firefox and Thunderbird. They are available here:
http://l10n.mozilla.org/pootle/pot/

As a start you might want to just use these POT files and gradually learn more
about the processes described below. Contact us for more help on using these.

.. _mozilla_l10n_scripts#requirements:

Requirements
============

* The :doc:`Translate Toolkit </index>` (>=1.3)
* All scripts in the ``tools/mozilla`` directory (from the project sources)
  should be executable and in your ``PATH``.

.. _build_ff3.1_langs.sh:

build_ff3.1_langs.sh
====================

.. _build_ff3.1_langs.sh#description:

Description
-----------
This is a simple bash script that embodies most of the Mozilla l10n process and
does the following:

#. Update Mozilla sources
#. Update language files from `Mozilla's L10n
   <http://hg.mozilla.org/l10n-central>`_ Mercurial repository.
#. Replace old l10n en-US files with a fresh copy from the updated source tree.
#. :doc:`Create new POT files </guides/creating_mozilla_pot_files>` from the
   :ref:`en-US <get_moz_enus.py>` l10n files.
#. Create archives of the POT files.
#. For each language:

   #. Update existing PO files if the checked out from a CVS, Subversion or
      Mercurial repository.
   #. :doc:`Migrate </guides/migrating_translations>` PO files to new POT
      files.
   #. :doc:`Create Mozilla l10n files <moz2po>` for the language based on the
      migrated PO files.
   #. Create archives of the PO files.
   #. :ref:`Build langpack <buildxpi.py>` for the
      language.

This script is used on the l10n.mozilla.org server to create most (if not all)
of the files available from http://l10n.mozilla.org/pootle/. It was originally
written as a stable way to provide these files and as such making it as general
as possible was not the biggest requirement. This is evident in the script's
very narrow focus.

.. _build_ff3.1_langs.sh#usage:

Usage
-----
This script takes no command-line parameters and is only configurable via the
variables at the top and, failing that, custom hacking of the script.

The variables are used in the following ways:

+--------------------+-------------------------------------------------------+
| ``BUILD_DIR``      | The base build directory from where building is done. |
+--------------------+-------------------------------------------------------+
| ``MOZCENTRAL_DIR`` | The directory containing a checkout of the Mozilla    |
|                    | source tree http://hg.mozilla.org/mozilla-central/    |
+--------------------+-------------------------------------------------------+
| ``HG_LANGS``       | A space-separated list of language codes to build     |
|                    | for.                                                  |
+--------------------+-------------------------------------------------------+
| ``L10N_DIR``       | The directory where Mozilla l10n files                |
|                    | (from l10n-central) should be collected.              |
+--------------------+-------------------------------------------------------+
| ``PO_DIR``         | The directory containing the externally-hosted or     |
|                    | previously available source PO files (e.g. PO files   |
|                    | managed in another VCS repository). It contains a     |
|                    | sub-directory for each language.                      |
+--------------------+-------------------------------------------------------+
| ``POPACK_DIR``     | The output directory for PO archives.                 |
+--------------------+-------------------------------------------------------+
| ``PORECOVER_DIR``  | The directory to put recovered PO files in. It        |
|                    | contains a sub-directory for each language.           |
+--------------------+-------------------------------------------------------+
| ``POT_INCLUDES``   | A space-separated list of files to be included in POT |
|                    | archives.                                             |
+--------------------+-------------------------------------------------------+
| ``POTPACK_DIR``    | The output directory for POT archives.                |
+--------------------+-------------------------------------------------------+
| ``POUPDATED_DIR``  | The directory to use for updated PO files. It         |
|                    | contains a sub-directory for each language.           |
+--------------------+-------------------------------------------------------+
| ``LANGPACK_DIR``   | The directory to put langpacks (XPIs) in.             |
+--------------------+-------------------------------------------------------+
| ``FF_VERSION``     | The version of Firefox that is being built for. This  |
|                    | is used in the file names of archives.                |
+--------------------+-------------------------------------------------------+

.. note:: It is **strongly** recommended that you mirror the directory
   structure specified by the default values of the ``*_DIR`` variables. For
   example the default value for ``L10N_DIR`` is ``${BUILD_DIR}/l10n``, then
   you should put your l10n-central check-outs in the ``l10n`` directory under
   your main build directory (``BUILD_DIR``).

   Basically, you should have an ideally separate build directory containing
   the following sub-directories: ``l10n``, ``mozilla-central``, ``po``,
   ``popacks``, ``potpacks``, ``po-updated`` and ``xpi`` (if used). This way
   the only variable that need to be changed is ``BUILD_DIR``.

.. _build_tb3_langs.sh:

build_tb3_langs.sh
==================
This is the script that the ``build_ff3.1_langs.sh`` script above was actually
adapted from. It is 90% similar with the obvious exception that it is aimed at
building Thunderbird 3.0 packages in stead of Firefox 3.1. Also note that this
script uses the comm-central repository in stead of mozilla-central.

.. _buildxpi.py:

buildxpi.py
===========

.. _buildxpi.py#description:

Description
-----------
Creates XPI language packs from Mozilla sources and translated l10n files. This
script has only been tested with Firefox 3.1 beta sources.

It is basically the scripted version of the process described on Mozilla's
`"Creating a language pack"
<https://developer.mozilla.org/en-US/docs/Creating_a_Language_Pack>`_ page.

This script is used by ``build_ff3.1_langs.sh`` to build language packs in its
final step.

.. note:: This script uses the ``.mozconfig`` file in your home directory. Any
   existing ``.mozconfig`` is renamed to ``.mozconfig.bak`` during operation
   and copied back afterwards.

.. _buildxpi.py#usage:

Usage
-----
::

  buildxpi.py [<options>] <lang> [<lang2> ...]

Example::

  buildxpi.py -L /path/to/l10n -s /path/to/mozilla-central -o /path/to/xpi_output af ar

Options:

-h, --help            show this help message and exit
-L L10NBASE, --l10n-base=L10NBASE
                      The directory containing the <lang> subdirectory.
-o OUTPUTDIR, --output-dir=OUTPUTDIR
                      The directory to copy the built XPI to (default:
                      current directory).
-p MOZPRODUCT, --mozproduct=MOZPRODUCT
                      The Mozilla product name (default: "browser").
-s SRCDIR, --src=SRCDIR
                      The directory containing the Mozilla l10n sources.
-d, --delete-dest     Delete output XPI if it already exists.
-v, --verbose         Be more noisy

.. _get_moz_enus.py:

get_moz_enUS.py
===============

.. _get_moz_enus.py#description:

Description
-----------
A simple script to collect the en-US l10n files from a Mozilla source tree
(``'comm-central``' or ``'mozilla-central``') by traversing the product's
``l10n.ini`` file.

.. _get_moz_enus.py#usage:

Usage
-----

::

  get_moz_enUS.py [options]

Options:

-h, --help            show this help message and exit
-s SRCDIR, --src=SRCDIR
                      The directory containing the Mozilla l10n sources.
-d DESTDIR, --dest=DESTDIR
                      The destination directory to copy the en-US locale
                      files to.
-p MOZPRODUCT, --mozproduct=MOZPRODUCT
                      The Mozilla product name.
--delete-dest         Delete the destination directory (if it exists).
-v, --verbose         Be more noisy

.. _moz-l10n-builder#deprecated:

moz-l10n-builder
================
This is the pre-Mercurial build script originally written by Dwayne Bailey.
This is the script that all the others on this page replaces for post-CVS
Mozilla l10n.

.. note:: This script is **not** applicable to the l10n process of any Mozilla products after the move to Mercurial.

For more information about this script see its :doc:`dedicated page
<moz-l10n-builder>`.

.. _moz_l10n_builder.py:

moz_l10n_builder.py
===================
This script was intended to be a simple and direct port of the
``moz-l10n-builder`` script from above. It has pro's and cons in comparison to
the original, but is very similar for the most part. So for more information
about this script, see the original script's :doc:`page <moz-l10n-builder>`.
