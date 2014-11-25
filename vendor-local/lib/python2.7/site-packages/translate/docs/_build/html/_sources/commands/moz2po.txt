
.. _moz2po:
.. _po2moz:

moz2po
******

moz2po converts Mozilla files to PO files.  It wraps converters that handle
.properties, .dtd and some strange Mozilla files.  The tool can work with files
from Mozilla's Mercurial repository.  The tools
thus provides a complete roundtrip for Mozilla localisation using PO files and
PO editors.

.. note:: This page should only be used as a reference to the command-line
   options for moz2po and po2moz. For more about using the Translate Toolkit
   and PO files for translating Mozilla products, please see the page on
   :doc:`mozilla_l10n_scripts`.

.. _moz2po#usage:

Usage
=====

::

  moz2po [options] <dir> <po>
  po2moz [options] <po> <dir>

Where:

+---------+---------------------------------------------------+
| <dir>   | is a directory containing valid Mozilla files     |
+---------+---------------------------------------------------+
| <po>    | is a directory of PO or POT files                 |
+---------+---------------------------------------------------+

.. program:: moz2po

Options (moz2po):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-iINPUT, --input=INPUT    read from INPUT in inc, it, \*, dtd, properties formats
-xEXCLUDE, --exclude=EXCLUDE   exclude names matching EXCLUDE from input paths
-oOUTPUT, --output=OUTPUT   write to OUTPUT in it.po, it.pot, manifest, xhtml.po, xhtml.pot, ini.po, ini.pot, rdf, js, \*, html.po, html.pot, inc.po, inc.pot, dtd.po, dtd.pot, properties.po, properties.pot formats
-tTEMPLATE, --template=TEMPLATE   read from TEMPLATE in it, \*, properties, dtd, inc formats
-S, --timestamp       skip conversion if the output file has newer timestamp
-P, --pot            output PO Templates (.pot) rather than PO files (.po)
--duplicates=DUPLICATESTYLE
                      what to do with duplicate strings (identical source
                      text): :doc:`merge, msgctxt <option_duplicates>`
                      (default: 'msgctxt')

.. program:: po2moz

Options (po2moz):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-iINPUT, --input=INPUT   read from INPUT in dtd.po, dtd.pot, ini.po, ini.pot, inc.po, inc.pot, manifest, it.po, it.pot, \*, html.po, html.pot, js, rdf, properties.po, properties.pot, xhtml.po, xhtml.pot formats
-xEXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-oOUTPUT, --output=OUTPUT     write to OUTPUT in dtd, \*, inc, it, properties formats
-tTEMPLATE, --template=TEMPLATE  read from TEMPLATE in dtd, \*, inc, it, properties formats
-S, --timestamp       skip conversion if the output file has newer timestamp
-lLOCALE, --locale=LOCALE  set output locale (required as this sets the directory names)
--removeuntranslated  remove untranslated strings from output
--threshold=PERCENT  only convert files where the translation completion is above PERCENT
--fuzzy              use translations marked fuzzy
--nofuzzy            don't use translations marked fuzzy (default)

.. _moz2po#examples:

Examples
========

.. _moz2po#creating_pot_files:

Creating POT files
------------------

.. seealso:: :doc:`Creating Mozilla POT files
   </guides/creating_mozilla_pot_files>`.

After extracting the en-US l10n files, you can run the following command::

  moz2po -P l10n/en-US pot

This creates a set of POT (:opt:`-P`) files in the ``pot`` directory from the
Mozilla files in ``l10n/en-US`` for use as PO Templates.

If you want to create a set of POT files with another base language try the
following::

  moz2po -P l10n/fr-FR fr-pot

This will create a set of POT files in ``fr-pot`` that have French as your
source language.

.. _moz2po#creating_po_files_from_existing_non-po_translations:

Creating PO files from existing non-PO translations
---------------------------------------------------

If you have existing translations (Mozilla related or other Babelzilla files)
and you wish to convert them to PO for future translation then the following
generic instructions will work::

  moz2po -t en-US af-ZA af-ZA_pofiles

This will combine the untranslated template en-US files from ``en-US`` combine
them with your existing translations in ``af-ZA`` and output PO files to
``af-ZA_pofiles``. ::

  moz2po -t l10n/fr l10n/xh po/xh

For those who are not English fluent you can do the same with another
languages.  In this case ``msgid`` will contain the French text from
``l10n/fr``.  This is useful for translating where the translators other
languages is not English but French, Spanish or Portuguese.  Please make sure
that the source languages i.e. the ``msgid`` language is fully translated as
against en-US.

.. _moz2po#creating_mercurial_ready_translations:

Creating Mercurial ready translations
-----------------------------------------

::

  po2moz -t l10n/en-US po/xh l10n/xh

Create Mozilla files using the templates files in ``l10n/en-US`` (see above for
how to create them) with PO translations in ``po/xh`` and ouput them to
``l10n/xh``.  The files now in ``l10n/xh`` are ready for submission to Mozilla
and can be used to build a language pack or translated version of Mozilla.

.. _moz2po#issues:

Issues
======

You can perform the bulk of your work (99%) with moz2po.

Localisation of XHTML is not yet perfect, you might want to work with the files
directly.

:issue:`Issue 203 <203>` tracks the outstanding features which would allow
complete localisation of Mozilla including; all help, start pages, rdf files,
etc. It also tracks some bugs.

Accesskeys don't yet work in .properties files and in several cases where the
Mozilla .dtd files don't follow the normal conventions, for example in
``security/manager/chrome/pippki/pref-ssl.dtd.po``. You might also want to
check the files mentioned in this Mozilla bug `329444
<https://bugzilla.mozilla.org/show_bug.cgi?id=329444>`_ where mistakes in the
DTD-definitions cause problems in the matching of accelerators with the text.

You might want to give special attention to the following files since it
contains customisations that are not really translations.

* mail/chrome/messenger/downloadheaders.dtd.po
* toolkit/chrome/global/intl.properties.po

Also, all width, height and size specifications need to be edited with feedback
from testing the translated interfaces.

There are some constructed strings in the Mozilla code which we can't do much
about. Take good care to read the localisation notes. For an example, see
``mail/chrome/messenger/downloadheaders.dtd.po``. In that specific file, the
localisation note from the DTD file is lost, so take good care of those.

The file extension of the original Mozilla file is required to tell the Toolkit
how to do the conversion.  Therefore, a file like foo.dtd must be named
foo.dtd.po in order to :doc:`po2moz <moz2po>` to recognise it as a DTD file.

