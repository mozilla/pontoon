
.. _poconflicts:

poconflicts
***********

poconflicts takes a PO file and creates an set of output PO files that contain
messages that conflict.  During any translation project that involves a large
amount of work or a number of translators you will see message conflicts.  A
conflict is where the same English message has been translated differently (in
some languages this may have been intentional).  Conflicts occur due to
different translation style or a shift in translations as the translators or
project mature.

poconflicts allows you to quickly identify these problem messages, investigate
and correct them. To merge the files back, they have to be restructured into
the correct directory structure using :doc:`porestructure` in order to enable
merging using :doc:`pomerge`.

.. _poconflicts#usage:

Usage
=====

::

  poconflicts [options] <po> <conflicts>

Where:

+-------------+--------------------------------------------------------------+
| <po>        | is a directory of existing PO files or an individual PO file |
+-------------+--------------------------------------------------------------+
| <conflicts> | is a directory containing one PO file for each conflict      |
+-------------+--------------------------------------------------------------+

Options:

--version            show program's version number and exit
-h, --help           show this help message and exit
--manpage            output a manpage based on the help
--progress=PROGRESS    show progress as: :doc:`dots, none, bar, names, verbose <option_progress>`
--errorlevel=ERRORLEVEL
                      show errorlevel as: :doc:`none, message, exception,
                      traceback <option_errorlevel>`
-iINPUT, --input=INPUT   read from INPUT in po format
-xEXCLUDE, --exclude=EXCLUDE  exclude names matching EXCLUDE from input paths
-oOUTPUT, --output=OUTPUT  write to OUTPUT in po format
-I, --ignore-case    ignore case distinctions
-v, --invert         invert the conflicts thus extracting conflicting destination words
--accelerator=ACCELERATORS
                      ignores the given :doc:`accelerator characters <option_accelerator>` when matching

.. _poconflicts#examples:

Examples
========

Here are some examples that demonstrate the usefulness of poconflict ::

  poconflicts --accelerator=~ -I xhosa conflicts

This extracts messages from the PO files in the *xhosa* directory and places a
new PO file for each identified conflict in *conflicts*.  We are working with
OpenOffice files and we therefore use the tilde (*~*) as the accelerator marker
(with this set *F~ile* is considered the same as *~File*).  We are also
ignoring the case of the message using :opt:`-I` (thus *File* is considered the
same as *file* or *FILE*)

Another useful option is to look at the inverted conflicts.  This will detect
target words that have been used to translate different source words. ::

  poconflicts --accelerator=~ -I -v xhosa conflicts

Now in the *conflicts* directory we will find PO files based on the Xhosa word.
We can now check where a Xhosa word has been used for different source or
English words.  Often there is no problem but you might find cases where the
same Xhosa word was used for Delete and Cancel -- clearly a usability issue.

The translator makes the needed corrections to the files and then we can
proceed to merge the results back into the PO files. Unchanged entries can be
removed.

Now restructure the files to resemble the original directory structure using
:doc:`porestructure`::

  porestructure -i conflicts -o conflicts_tree

Now merge the changes back using pomerge::

  pomerge -t xhosa -i conflicts_tree -o xhosa

This takes the corrected files from *conflicts_tree* and merge them into the
files in *xhosa* using the same files as templates.
