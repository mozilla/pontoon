
.. _prop2po:
.. _po2prop:

prop2po
*******

Convert between Java property files (.properties) and Gettext PO format.

Note: this tool completely eliminates the need for :ref:`native2ascii
<prop2po#doing_away_with_native2ascii>` as po2prop does the correct escaping to
the Latin1 encoding that is needed by Java.

The following other formats are also supported via the :doc:`--personality
<option_personality>` parameter:

* Adobe Flex
* Skype .lang
* Mac OS X .strings
* Mozilla .properties

.. _prop2po#usage:

Usage
=====

::

  prop2po [options] <property> <po>
  po2prop [options] -t <template> <po> <property>

Where:

+------------+-----------------------------------------------------------+
| <property> | is a directory containing property files or an individual |
|            | property file                                             |
+------------+-----------------------------------------------------------+
| <po>       | is a directory containing PO files and an individual      |
|            | property file                                             |
+------------+-----------------------------------------------------------+
| <template> | is a directory of template property files or a single     |
|            | template property file                                    |
+------------+-----------------------------------------------------------+

Options (prop2po):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-iINPUT, --input=INPUT   read from INPUT in properties format
-xEXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-oOUTPUT, --output=OUTPUT  write to OUTPUT in po, pot formats
-tTEMPLATE, --template=TEMPLATE   read from TEMPLATE in properties format
-S, --timestamp       skip conversion if the output file has newer timestamp
-P, --pot            output PO Templates (.pot) rather than PO files (.po)
--personality=TYPE    override the input file format: :doc:`flex, java, mozilla,
                      java-utf8, skype, gaia, strings <option_personality>`
                      (for .properties files, default: java)
--encoding=ENCODING  override the encoding set by the personality
--duplicates=DUPLICATESTYLE
                      what to do with duplicate strings (identical source
                      text): :doc:`merge, msgctxt <option_duplicates>`
                      (default: 'msgctxt')

Options (po2prop):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-iINPUT, --input=INPUT   read from INPUT in po, pot formats
-xEXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-oOUTPUT, --output=OUTPUT  write to OUTPUT in properties format
-tTEMPLATE, --template=TEMPLATE  read from TEMPLATE in properties format
-S, --timestamp       skip conversion if the output file has newer timestamp
--personality=TYPE    override the input file format: :doc:`flex, java, mozilla,
                      java-utf8, skype, gaia, strings <option_personality>`
                      (for .properties files, default: java)
--encoding=ENCODING  override the encoding set by the personality (since 1.8.0)
--removeuntranslated  remove key value from output if it is untranslated
--threshold=PERCENT  only convert files where the translation completion is above PERCENT
--fuzzy              use translations marked fuzzy
--nofuzzy            don't use translations marked fuzzy (default)

.. _prop2po#examples:

Examples
========

These examples demonstrate most of the useful invocations of prop2po:

.. _prop2po#creating_pot_files:

Creating POT files
------------------

::

  prop2po -P properties pot

Extract messages from *properties* directory and place them in a directory
called *pot*.  The :opt:`-P` option ensures that we create POT files instead of
PO files.::

  prop2po -P file.properties file.pot

Extract messages from *file.properties* and place them in *file.pot*.

.. _prop2po#creating_po_files_from_existing_work:

Creating PO files from existing work
------------------------------------

::

  prop2po --duplicates=msgctxt -t reference zu zu-po

Extract all existing Zulu messages from *zu* directory and place the resultant
PO files in a directory called *zu-po*.  If you find duplicate messages in a
file then use Gettext's mgsctxt to disambiguate them.  During the merge we use
the .properties files in *reference* as templates and as the source of the
English text for the msgid.  Once you have your PO files you might want to use
:doc:`pomigrate2` to ensure that your PO files match the latest POT files.

.. _prop2po#creating_.properties_files_from_your_translations:

Creating .properties files from your translations
-------------------------------------------------

::

  po2prop -t reference zu-po zu

Using our translations found in *zu-po* and the templates found in *reference*
we create a new set of property files in *zu*.  These new property files will
look exactly like those found in the templates, but with the text changed to
the translation.  Any fuzzy entry in our PO files will be ignored and any
untranslated item will be placed in *zu* in English.  The .properties file
created will be based on the Java specification and will thus use escaped
Unicode.  Where::

  ṽḁḽṻḝ

Will appear in the files as::

  \u1E7D\u1E01\u1E3D\u1E7B\u1E1D

To get output as used by Mozilla localisation do the following::

  po2prop --personality=mozilla -t reference zu-po zu

This will do exactly the same as above except that the output will now appear
as real Unicode characters in UTF-8 encoding.

.. _prop2po#doing_away_with_native2ascii:

Doing away with native2ascii
============================

The `native2ascii
<http://docs.oracle.com/javase/7/docs/technotes/tools/windows/native2ascii.html>`_
command is the traditional tool of property file localisers.  With prop2po
there is no need to use this command or to ever work directly with the escaped
Unicode.

If you are working mostly with Gettext PO files then this is a double benefit
as you can now use your favourite PO editor to translate Java applications.
Your process would now look like this::

  prop2po some.properties some.po

Firstly create a PO file that you can translate.  Now translate it in your
favourite PO editor.::

  po2prop -t some.properties some.po some-other.properties

Using the original properties file as a template we preserve all layout and
comments, combined with your PO translation we create a new translate
properties file.  During this whole process we have not needed to understand or
process any escaping prop2po and po2prop handle that all automatically.

If you have existing translations you can recover them as follows::

  prop2po -t some.properties translations.properties translations.po

This takes the default English properties file and combines it with your
translate properties file and created a PO file.  You now continue translating
using your PO file.
