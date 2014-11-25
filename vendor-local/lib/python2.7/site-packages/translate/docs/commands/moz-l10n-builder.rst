
.. _moz-l10n-builder:

moz-l10n-builder
****************

Take a set of Mozilla (Firefox, Thunderbird, SeaMonkey, etc.) localisation and
migrate them to the latest Mozilla source, building XPIs and repackaging hte
Windows .exe file as needed.

Please also check the page on `creating a language pack
<https://developer.mozilla.org/en/docs/Creating_a_Language_Pack>`_ on the
Mozilla wiki, to stay abreast of the latest Mozilla way of doing things.

.. note:: This page is only applicable to Mozilla products with its source
   hosted in CVS. This includes Firefox versions before 3.1 and Thunderbird
   versions before 3.0.

   For information about working with the new source trees in Mercurial, see the :doc:`mozilla_l10n_scripts` page.

.. _moz-l10n-builder#prerequisites:

Prerequisites
=============

* Translation update component and building XPIs

  * :doc:`Translate Toolkit </installation>`
  * Existing Mozilla translations in PO format
  * A checkout of `Mozilla sources
    <https://developer.mozilla.org/en-US/docs/Developer_Guide/Source_Code/CVS>`_
    updated to the correct `BRANCH or RELEASE
    <https://developer.mozilla.org/en/docs/CVS_Tags>`_

* Building Windows executables

  * Firefox or Thunderbird `en-US .exe
    <http://releases.mozilla.org/pub/mozilla.org/firefox/releases/>`_ file e.g.
    `Firefox 2.0 en-US
    <http://releases.mozilla.org/pub/mozilla.org/firefox/releases/2.0/win32/en-US/Firefox%20Setup%202.0.exe>`_
  * `upx <http://upx.sourceforge.net/>`_ for executable compression
  * `Nullsoft installer <http://nsis.sourceforge.net/Main_Page>`_ to package
    the installer.
  * `7zip <http://www.7-zip.org/>`_ for various compression
  * Linux: `WINE <http://www.winehq.org/>`_ to run the Nullsoft installer

* Directory structure under the directory you want to run moz-l10n-builder in:

+-----------+--------------------------------------------------------------+
| l10n/     | Contains Mozilla l10n files for available/needed language(s) |
+-----------+--------------------------------------------------------------+
| mozilla/  | The Mozilla source tree                                      |
+-----------+--------------------------------------------------------------+
| po/       | Contains your PO files (output from moz2po)                  |
+-----------+--------------------------------------------------------------+
| potpacks/ | Where POT-archives go                                        |
+-----------+--------------------------------------------------------------+

Note these instructions are for building on Linux, they may work on Windows.
All software should be available through your distribution.  You will need to
use Wine to install the Nullsoft installer and may need to sort out some path
issues to get it to run correctly.

.. _moz-l10n-builder#latest_version:

Latest Version
==============

moz-l10n-builer is not currently distributed as part of the toolkit.  You can
get the `latest version from Git
<https://raw.github.com/translate/translate/master/tools/mozilla/moz-l10n-builder>`_
and you will also need this `minor patch
<https://raw.github.com/translate/translate/master/tools/mozilla/mozilla-l10n.patch>`_
to the mozilla source code.

.. _moz-l10n-builder#usage:

Usage
=====

::

  moz-l10n-builder [language-code|ALL]

Where:

+----------------+-----------------------------------------------------------+
| language-code  | build only the supplied languages, or build ALL if        |
|                | specified or if no option is supplied                     |
+----------------+-----------------------------------------------------------+

Your translations will not be modified.

.. _moz-l10n-builder#operation:

Operation
=========

moz-l10n-builder does the following:

* Updates the mozilla/ directory
* Creates POT files
* Migrates your translations to this new POT file
* Converts the migrated POT files to .dtd and .properties files
* Builds XPI and .exe files
* Performs various hacks to cater for the anomalies of file formats
* Outputs a diff of you migrated PO files and your newly generated Mozilla
  l10n/ files

.. _moz-l10n-builder#bugs:

Bugs
====

Currently it is too Translate.org.za specific and not easily configurable
without editing.  It is also not intelligent enough to work our that you want
Firefox vs Thunderbird generation.  A lot of this functionality should be in
the Mozilla source code itself.  We hope over time that this might happen.
