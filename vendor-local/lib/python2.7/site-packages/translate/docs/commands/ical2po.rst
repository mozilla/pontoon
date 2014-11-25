
.. _ical2po:
.. _po2ical:

ical2po
*******

.. versionadded:: 1.2

Converts iCalendar (\*.ics) files to Gettext PO format.

.. _ical2po#usage:

Usage
=====

::

  ical2po [options] <ical> <po>
  po2ical [options] -t <ical> <po> <ical>

Where:

+---------+---------------------------------------------------+
| <ical>  | is a valid .ics file or directory of those files  |
+---------+---------------------------------------------------+
| <po>    | is a directory of PO or POT files                 |
+---------+---------------------------------------------------+

Options (ical2po):

--version           show program's version number and exit
-h, --help          show this help message and exit
--manpage           output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT      read from INPUT in php format
-x EXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT     write to OUTPUT in po, pot formats
-t TEMPLATE, --template=TEMPLATE  read from TEMPLATE in php format
-S, --timestamp       skip conversion if the output file has newer timestamp
-P, --pot    output PO Templates (.pot) rather than PO files (.po)
--duplicates=DUPLICATESTYLE
                      what to do with duplicate strings (identical source
                      text): :doc:`merge, msgctxt <option_duplicates>`
                      (default: 'msgctxt')

Options (po2ical):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-i INPUT, --input=INPUT  read from INPUT in po, pot formats
-x EXCLUDE, --exclude=EXCLUDE   exclude names matching EXCLUDE from input paths
-o OUTPUT, --output=OUTPUT      write to OUTPUT in php format
-t TEMPLATE, --template=TEMPLATE  read from TEMPLATE in php format
-S, --timestamp      skip conversion if the output file has newer timestamp
--threshold=PERCENT  only convert files where the translation completion is above PERCENT
--fuzzy              use translations marked fuzzy
--nofuzzy            don't use translations marked fuzzy (default)

.. _ical2po#examples:

Examples
========

This example looks at roundtrip of iCalendar translations. While you can do
recovery of translations, its unlikely that you will ever need to do that.

First we need to create a set of POT files. ::

  ical2po -P ical.ics ical.pot

The ical.ics file is converted to Gettext POT files called ical.pot.
Directories of iCalendar files can also be processed.

Begin translating the ical.pot file by first copying it to make a PO file. ::

  cp ical.pot ical-af.po

You are now in a position to translate the file ical-af.po in your favourite
translation tool.

Once translated you can convert back as follows::

  po2ical -t ical.ics ical-af.po ical-af.ics

Your translations found in the Afrikaans PO file, ``ical-ad.po``, will be
converted to .ics using the file ``ical.ics`` as a template and creating your
newly translated .ics file ``ical-af.ics``.

To update your translations simply redo the POT creation step and make use of
:doc:`pot2po` to bring your translation up-to-date.

.. _ical2po#notes:

Notes
=====

The converter will only process events in the calender file, the file itself
can contain many other things that could be localisable.  Please raise a bug if
you want to extract additional items.

The converter does not make use of the LANGUAGE attribute which is permitted in
the format.  The LANGUAGE attribute does not aid multilingualism in this
context so is ignored.

The converter could conceivably also process :wp:`vCard <Vcard>` files, but
this has not been implemented for lack of a clear need.  Please raise a bug
with an example if you have such a file that could benefit from localisation.
