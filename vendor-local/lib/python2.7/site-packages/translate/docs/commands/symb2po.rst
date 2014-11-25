
.. _symb2po:
.. _po2symb:

symb2po
*******

.. versionadded:: 1.3

Converts Symbian-style translation files to PO files and vice versa. The
Symbian translation files currently have a strong Buddycloud flavour, but the
tools will be made more general as the need arises.

.. _symb2po#usage:

Usage
=====

::

  symb2po [options] [-t <target_lang_symb>] <source_lang_symb> <po>
  po2symb [options] -t <target_lang_symb> <po> <target_lang_symb>

Where:

+--------------------+-------------------------------------------------------+
| <target_lang_symb> | is a valid Symbian translation file or directory of   |
|                    | those files                                           |
+--------------------+-------------------------------------------------------+
| <source_lang_symb> | is a valid Symbian translation file or directory of   |
|                    | those files                                           |
+--------------------+-------------------------------------------------------+
| <po>               | is a PO or POT file or a directory of PO or POT files |
+--------------------+-------------------------------------------------------+

Options (symb2po):

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
-t TEMPLATE, --template=TEMPLATE  read from TEMPLATE in the Symbian translation format
-S, --timestamp      skip conversion if the output file has newer timestamp
-P, --pot    output PO Templates (.pot) rather than PO files (.po)
--duplicates=DUPLICATESTYLE
                      what to do with duplicate strings (identical source
                      text): :doc:`merge, msgctxt <option_duplicates>`
                      (default: 'msgctxt')

Options (po2symb):

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
-t TEMPLATE, --template=TEMPLATE  read from TEMPLATE in the Symbian translation format
-S, --timestamp      skip conversion if the output file has newer timestamp

.. _symb2po#examples:

Examples
========

.. _symb2po#symb2po:

symb2po
-------

The most common use of symb2po, is to generate a POT (PO template) file from
the English translation (note that the tool currently expects the Symbian
translation file to end with the extension .r01, which is the code for English
translation files). This file then serves as the source document from which all
translations will be derived.

To create a POT file called ``my_project.pot`` from the source Symbian
translation file ``my_project.r01``, the following is executed::

  symb2po my_project.r01 my_project.pot

In order to re-use existing translations in the Symbian translation format,
symb2po can merge that translation into the source Symbian translation to
produce a translated PO file. The existing Symbian translation file is
specified with the :opt:`-t` flag.

To create a file called ``my_project-en-fr.po`` (this is not the recommended PO
naming convention) from the source Symbian translation file ``my_project.r01``
and its French translation ``my_project.r02``, execute::

  symb2po -t my_project.r02 my_project.r01 my_project-en-fr.po

.. note:: Ensure that the English and French files are well aligned, in other
   words, no changes to the source text should have happened since the
   translation was done.

.. _symb2po#po2symb:

po2symb
-------

The po2symb tool is used to extract the translations in a PO into a template
Symbian translation file. The template Symbian translation file supplies the
"shape" of the generated file (formatting and comments).

In order to produce a French Symbian translation file using the English Symbian
translation file ``my_project.r01`` as a template and the PO file
``my_project-en-fr.po`` (this is not the recommended PO naming convention) as
the source document, execute::

  po2symb -t my_project.r01 my_project-en-fr.po my_project.r02

.. _symb2po#notes:

Notes
=====

The tools won't touch anything appearing between lines marked as::

  // DO NOT TRANSLATE

The string ``r_string_languagegroup_name`` is used to set the ``Language-Team``
PO header field.

The Symbian translation header field ``Author`` is used to set the
``Last-Translator`` PO header field.

.. _symb2po#issues:

Issues
======

The file format is heavily tilted towards the Buddycould implementation

The tools do nothing with the ``Name`` and ``Description`` Symbian header
fields. This means that ``po2symb`` will just copy the values in the supplied
template. So you might see something such as::

  Description : Localisation File : English

in a generated French translation file.

.. _symb2po#bugs:

Bugs
====

Probably many, since this software hasn't been tested much yet.
