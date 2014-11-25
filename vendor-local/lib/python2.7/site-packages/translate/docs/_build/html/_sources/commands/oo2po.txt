
.. _oo2po:
.. _po2oo:
.. _oo2xliff:
.. _xliff2oo:

oo2po
*****

Convert between OpenOffice.org GSI/SDF files and the PO format.  This tool
provides a complete roundtrip; it preserves the structure of the GSI file and
creates completely valid PO files.

oo2xliff will convert the SDF files to XLIFF format.

.. _oo2po#usage:

Usage
=====

::

  oo2po [options] <sdf> <output>
  po2oo [options] [-t <en-US.sdf>] -l <targetlang> <input> <sdf|output>

or for XLIFF files::

  oo2xliff [options] -l <targetlang> <sdf> <output>
  xliff2oo [options] [-t <en-US.sdf>] -l <targetlang> <input> <sdf|output>

Where:

+--------------+-----------------------------------------------------------+
| <sdf>        | is a valid OpenOffice.org GSI or SDF files                |
+--------------+-----------------------------------------------------------+
| <output>     | is a directory for the resultant PO/POT/XLIFF files       |
+--------------+-----------------------------------------------------------+
| <input>      | is a directory of translated PO/XLIFF files               |
+--------------+-----------------------------------------------------------+
| <targetlang> | is the :wp:`ISO 639 <ISO_639>` language code used in the  |
|              | sdf file, e.g. af                                         |
+--------------+-----------------------------------------------------------+

Options (oo2po and oo2xliff):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-iINPUT, --input=INPUT   read from INPUT in oo format
-xEXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-oOUTPUT, --output=OUTPUT  write to OUTPUT in po, pot formats
-S, --timestamp      skip conversion if the output file has newer timestamp
-P, --pot            output PO Templates (.pot) rather than PO files (.po) (only available in oo2po
-lLANG, --language=LANG  set target language to extract from oo file (e.g. af-ZA) (required for oo2xliff)
--source-language=LANG   set source language code (default en-US)
--nonrecursiveinput      don't treat the input oo as a recursive store
--duplicates=DUPLICATESTYLE
                      what to do with duplicate strings (identical source
                      text): :doc:`merge, msgctxt <option_duplicates>`
                      (default: 'msgctxt')
--multifile=MULTIFILESTYLE
                      how to split po/pot files (:doc:`single, toplevel or
                      onefile <option_multifile>`)

Options (po2oo and xliff2oo):

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-iINPUT, --input=INPUT   read from INPUT in po, pot formats
-xEXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-oOUTPUT, --output=OUTPUT  write to OUTPUT in oo format
-tTEMPLATE, --template=TEMPLATE  read from TEMPLATE in oo format
-S, --timestamp          skip conversion if the output file has newer timestamp
-lLANG, --language=LANG  set target language code (e.g. af-ZA) [required]
--source-language=LANG   set source language code (default en-US)
-T, --keeptimestamp      don't change the timestamps of the strings
--nonrecursiveoutput     don't treat the output oo as a recursive store
--nonrecursivetemplate   don't treat the template oo as a recursive store
--filteraction=ACTION
                      action on pofilter failure: :doc:`none (default), warn,
                      exclude-serious, exclude-all <option_filteraction>`
--threshold=PERCENT      only convert files where the translation completion is above PERCENT
--fuzzy                  use translations marked fuzzy
--nofuzzy                don't use translations marked fuzzy (default)
--multifile=MULTIFILESTYLE
                      how to split po/pot files (:doc:`single, toplevel or
                      onefile <option_multifile>`)

.. _oo2po#examples:

Examples
========

These examples demonstrate most of the useful invocations of oo2po:

.. _oo2po#creating_pot_files:

Creating POT files
------------------

::

  oo2po -P en-US.sdf pot

Extract messages from *en-US.sdf* and place them in a directory called *pot*.
The :opt:`-P` option ensures that we create POT files instead of PO files. ::

  oo2po -P --source-language=fr fr-FR.sdf french-pot

Instead of creating English POT files we are now creating POT files that
contain French in the msgid.  This is useful for translators who are not
English literate.  You will need to have a fully translated sdf in the source
language.

.. _oo2po#creating_po_files_from_existing_work:

Creating PO files from existing work
------------------------------------

::

  oo2po --duplicates=merge -l zu zu-ZA.sdf zulu

Extract all existing Zulu (*zu*) messages from *zu-ZA.sdf* and place them in a
directory called *zulu*.  If you find duplicate messages in a file then merge
them into a single message (This is the default behaviour for traditional PO
files).  You might want to use :doc:`pomigrate2` to ensure that your PO files
match the latest POT files.::

  cat GSI_af.sdf GSI_xh.sdf > GSI_af-xh.sdf
  oo2po --source-language=af -l xh GSI_af-xh.sdf af-xh-po

Here we are creating PO files with your existing translations but a different
source language.  Firstly we combine the two SDF files.  Then oo2po creates a
set of PO files in *af-xh-po* using Afrikaans (*af*) as the source language and
Xhosa (*xh*) as the target language from the combined SDF file *GSI_af-xh.sdf*

.. _oo2po#creating_a_new_gsi/sdf_file:

Creating a new GSI/SDF file
---------------------------

::

  po2oo -l zu zulu zu_ZA.sdf

Using PO files found in *zulu* create an SDF files called *zu_ZA.sdf* for
language *zu*::

  po2oo -l af -t en-US.sdf --nofuzzy --keeptimestamp --filteraction=exclude-serious afrikaans af_ZA.sdf

Create an Afrikaans (*af*) SDF file called *af_ZA.sdf* using *en-US.sdf* as a
template and preserving the timestamps within the SDF file while also
eliminating any serious errors in translation.  Using templates ensures that
the resultant SDF file has exactly the same format as the template SDF file.
In an SDF file each translated string can have a timestamp attached.  This
creates a large amount of unuseful traffic when comparing version of the SDF
file, by preserving the timestamp we ensure that this does not change and can
therefore see the translation changes clearly.  We have included the *nofuzzy*
option (on by default) that prevent fuzzy PO messages from getting into the SDF
file.  Lastly the *filteraction* option is set to exclude serious errors:
variables failures and translated XML will be excluded from the final SDF.

.. _oo2po#helpcontent2:

helpcontent2
============

The escaping of ``helpcontent2`` from SDF files was very confusing,
:issue:`295` implemented a fix that appeared in version 1.1.0 (All known issues
were fixed in 1.1.1).  Translators are now able to translate helpcontent2 with
clean escaping.
