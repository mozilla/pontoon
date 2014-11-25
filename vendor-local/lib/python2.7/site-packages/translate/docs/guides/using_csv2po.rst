
.. _using_csv2po:

Using csv2po
************

:doc:`csv2po </commands/csv2po>` allows you to create CSV files from PO files.
This allows you to send translation work to translators who do not or cannot
use PO Editors but who can use a Spreadsheet.

.. _using_csv2po#quickstart:

Quickstart
==========

#. ``pofilter --fuzzy --review -t untranslated <po-dir> <po-filtered-dir>``
   (this step is optional)
#. divide into sections
#. ``po2csv <po-dir|po-filtered-dir> <csv-out>``
#. edit in Excel or OpenOffice.org Calc
#. ``csv2po --charset=windows-1250 -t templates <csv-in> <po-in>`` (you must
   work against a template directory, the charset option corrects problems with
   characters sets)
#. ``/commands/phase`` -- to do basic checks sort out encoding issues
#. ``pomerge --mergeblank=no -t <po-dir> <po-in> <po-dir>``
#. ``git diff`` --- check the changes
#. ``git add`` & ``git commit`` --- commit changes

.. _using_csv2po#detailed_description:

Detailed Description
====================

po2csv allows you to send CSV files, which can be edited in any spreadsheet, to
a translator.  This document outlines the process to follow from the raw po
files -> CSV files -> back to PO.  We also look at a case where you may have
submitted a subset of the PO files for translation and you need to integrate
these.

.. _using_csv2po#creating_a_subset:

Creating a subset
-----------------

This step is optional.

To send a translator only those messages that are untranslated, fuzzy or need
review run::

  pofilter --isfuzzy --isreview -t untranslated <po-dir> <po-filtered-dir>

.. _using_csv2po#divide_into_sections:

Divide into sections
--------------------

You might want to divide the work into sections if you are apportioning it to
different translators.  In that case create new directories::

  e.g. po-filtered-dir-1 po-filtered-dir-2
  or  po-filtered-dir-bob po-filtered-dir-mary

Copy files from *po-filtered-dir* to *po-filtered-dir-N* in a way that balance
the work or apportions the amounts you want for each translator.  Try to keep
sections together and not break them up to much e.g.  Give one translator all
the OpenOffice.org Calc work don't split it between two people -- this is just a
simple measure to ensure constancy.

Now continue as normal and convert to CSV and perform word counts for each
separate directory.

.. _using_csv2po#creating_the_csv_files:

Creating the CSV files
----------------------

::

  po2csv <po-dir|po-filtered-dir> <csv-out>

This will create a set of CSV files in *csv-out* which you can compress using
zip (we use zip because most people are Windows users)

.. _using_csv2po#creating_a_word_count:

Creating a word count
---------------------

Professional translators work on source word counts.  So we create a word count
to go with the file::

  pocount `find po-dir|po-filtered-dir -name "*.po"`

We work on source words regardless of whether the string is fuzzy or not.  You
might want to get a lower rate for work on fuzzy strings.

Place the word count file in both the PO and CSV directory to avoid the problem
of finding it later.  Check the number to make sure you haven't inadvertently
including something that you didn't want in.

.. _using_csv2po#package_the_csv_files:

Package the CSV files
---------------------

::

  zip -r9 work.zip <csv-out>

.. _using_csv2po#translating:

Translating
-----------

Translators can use most Spreadsheets. Excel works well.  However there are a
few problems with spreadsheets:

* Encoding -- you can sort that out later
* Strings that start with ' -- most spreadsheets treat cells starting with ' as
  text and gobble up the '.  A work around is to escape those like this \'.
  po2csv should do this for you.
* Autocorrect -- Excel changes ... to a single character and does other odd
  things.  pofilter will help catch these later.
* Sentences with + -- or +- will create errors and the translators will have to
  escape them as \+ \- \+-
* Sentences that only contain numbers can get broken: "1." will be converted to
  "1"

.. _using_csv2po#converting_excel_spreadsheets_to_csv_file:

Converting Excel spreadsheets to CSV file
-----------------------------------------

You can, and should, keep your files as CSV files.  However, many translators
are not the best wizzes at using their spreadsheet.  In this case many files
will have been changed to XLS files.  To convert them by hand is tedious and
error prone.  Rather make use of `xlHtml
<http://freecode.com/projects/xlhtml/>`_ which can do all the work for you.

::

  xlhtml -xp:0 -csv file.xls > file.csv

.. _using_csv2po#converting_csv_back_to_po:

Converting CSV back to PO
-------------------------

Extract the CSV files here we assume they are in *csv-in*::

  csv2po --charset=windows-1250 -t <templates> <csv-in> <po-in>

This will create new PO files in *po-in* based on the CSV files in the *csv-in*
and the template PO files in *templates*.  You shouldn't run the csv2po command
without templates as this allows you to preserve the original file layout.
Only run it without :opt:`-t` if you are dealing with a partial part of the PO
that you will merge back using a :doc:`/commands/pomerge`.

.. note:: Running csv2po using the input PO files as templates give spurious
   results.  It should probably be made to work but doesn't

.. note:: You might have encoding problems with the returned files. Use the
   :opt:`--charset` option to convert the file from another encoding (all PO
   files are created using UTF-8).  Usually Windows user will be using
   something like WINDOWS-1250. Check the file after conversion to see that
   characters are in fact correct if not try another encoding.

.. _using_csv2po#checking_the_new_po_files:

Checking the new PO files
-------------------------

Use :doc:`/commands/pofilter` to run checks against your new files. Read
:doc:`using_pofilter` to get a good idea of how to use the tool.

.. _using_csv2po#removing_fuzzies:

Removing fuzzies
----------------

When you merge work back that you know is good you want to make sure that it
overrides the fuzzy status of the existing translations, in order to do that
you need to remove the "#, fuzzy" markers.

This is best performed against CVS otherwise who knows what changed.

.. code-block:: bash

    po-in-dir=your-incomming-po-files
    po-dir=your-existing-po-files

    for pofile in `cd $po-in-dir; find . -name "\*.po"`
    do
           egrep -v "^#, fuzzy" < $po-dir/$pofile > $po-dir/${pofile}.unfuzzy && \
           mv $po-dir/${pofile}.unfuzzy $po-dir/$pofile
    done

.. _using_csv2po#merging_po_files_into_the_main_po_files:

Merging PO files into the main PO files
---------------------------------------

This step would not be necessary if the CSV contained the complete PO file.  It
is only needed when the translator has been editing a subset of the whole PO
file. ::

  pomerge --mergeblank=no -t po-dir -i po-in -o po-dir

This will take PO files from *po-in* merge them with those in *po-dir* using
*po-dir* as the template -- i.e. overwriting files in *po-dir*. It will also
ignore entries that have blank msgstr's i.e. it will not merge untranslated
items. The default behaviour of pomerge is to take all changes from *po-in* and
apply them to *po-dir* by overriding this we can ignore all untranslated items.

There is no option to override the status of the destination PO files with that
of the input PO.  Therefore all your entries that were fuzzy in the destination
will still be fuzzy even thought the input was corrected.  If you are confident
that all your input is correct then relook at the previous section on removing
fuzzies.
