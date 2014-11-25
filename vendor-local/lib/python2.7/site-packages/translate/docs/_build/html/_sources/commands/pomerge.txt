
.. _pomerge:

pomerge
*******

Pomerge will merge corrected PO, XLIFF, or TMX files (or snippets) into your
existing PO, XLIFF, TMX files.  Usually you would extract errors using
:doc:`pofilter`, make corrections to these PO (or XLIFF, TMX) snippets then
merge them back using pomerge.  You could also use :doc:`pogrep` to extract a
number of messages matching a certain string, make corrections then merge the
correction back using pomerge.

It is probably best to run pomerge against files stored in some kind of version
control system so that you can monitor what changes were made.

Pomerge will also attempt to make as small a change as possible to the text,
making it easier to see the changes using your version control system.

.. _pomerge#usage:

Usage
=====

::

  pomerge [options] [-t <template>] -i <input> -o <output>

Where:

+------------+--------------------------------------------------------------+
| <template> | is a set of reference PO, XLIFF, TMX files, either the       |
|            | originals or a set of POT files                              |
+------------+--------------------------------------------------------------+
| <input>    | contains the corrected files that are to override content in |
|            | <output>                                                     |
+------------+--------------------------------------------------------------+
| <output>   | contains the files whose content will be overridden by       |
|            | <input>.  This can be the same directory as <template>       |
+------------+--------------------------------------------------------------+

Options:

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-iINPUT, --input=INPUT   read from INPUT in po, pot, xlf, tmx formats
-xEXCLUDE, --exclude=EXCLUDE   exclude names matching EXCLUDE from input paths
-oOUTPUT, --output=OUTPUT   write to OUTPUT in po, pot, xlf, tmx formats
-tTEMPLATE, --template=TEMPLATE   read from TEMPLATE in po, pot, xlf, tmx formats
--mergeblanks=MERGEBLANKS  whether to overwrite existing translations with blank translations (yes/no). Default is yes.
--mergefuzzy=MERGEFUZZY  whether to overwrite existing translations with fuzzy translations (yes/no). Default is yes. (new in version 1.9)
--mergecomments=MERGECOMMENTS  whether to merge comments as well as translations (yes/no). Default is yes.

.. _pomerge#examples:

Examples
========

These examples show pomerge in action. ::

  pomerge -t af -i af-check -o af

Take corrections from *af-check* merge them with the templates in *af* and
output into *af*.  Thus merge af-check and override entries found in *af*.  Do
this only if you are using a version control system so that you can check
what changes pomerge made or if you have complete and utter confidence in this
tool. ::

  pomerge --mergeblanks=yes -t af -i af-check -o af-new

Merge the corrections from *af-check* with templates in *af* and output to
*af-new*.  If an entry is blank in *af-check* then make it blank in the output
in *af-new*.

.. _pomerge#issues:

Issues
======

* Seems to have trouble merging KDE style comments back. (Probably not relevant
  with newest versions any more.)
* Only files found in the input directory will be copied to the output. The
  template directory is not searched for extra files to copy to the output.
  Therefore it is always best to have your input directory in version control,
  and use the same directory as output. This will allow you to use the diff
  function of the version control system to double check changes made, with all
  the files of the input still present.

