
.. _using_pofilter:
.. _checking_your_files_with_po_filter:

Checking your files with PO filter
**********************************

:doc:`/commands/pofilter` allows you to check your PO or XLIFF files for
certain common errors.  This quick-start guide takes you through the process of
using this tool, making corrections and merging your correction back into your
translations.

The toolkit also other tools that can assist with :ref:`quality assurance
<commands#quality_assurance>`.

.. _using_pofilter#quickstart:

Quickstart
==========

*Use any preferred text editor wherever* ``vim`` *is used.*

#. Select filter(s): ``pofilter -l``
#. Run filter(s): ``pofilter -i existing_files/ -o errors/ [-t specific tests]
   [--excludefilter don't perform specific tests]``
#. Delete items you don't want changed, set fuzzy if needed, delete if not
   needed: ``vim errors/*.po``
#. Merge changes back: ``pomerge -i errors/ -o existing_files/ -t
   existing_files/`` (will overwrite existing files)
#. Create a patch for the changes: ``cvs diff -u existing_files/ > x.diff``
#. Check to see that the updates are what you want: ``vim x.diff``
#. Commit changes: ``cvs ci existing_files/``

.. _using_pofilter#detailed_description:

Detailed Description
====================

:doc:`/commands/pofilter` runs a number of checks against your translation
files.  Any messages that fail are output to a set of new files (in the same
structure as the source/input files).  You then edit these new/output files to
correct any errors.  Once you are satisfied with your corrections these
corrected files are then merged back into the original files using
:doc:`/commands/pomerge`.

.. _using_pofilter#extracting_errors:

Extracting Errors
-----------------

pofilter will run all tests unless you use the :opt:`-t` or
:opt:`--excludefilter` options.  There are over :doc:`38 tests
</commands/pofilter_tests>` and pofilter can itself provide you with a current
list of all the available checks::

  pofilter -l

We want to run the: accelerators, escapes, variables and xmltags tests as these
are the ones most likely to break programs at runtime.  We are also working
with OpenOffice.org PO files created using :doc:`/commands/oo2po` so we want to
ensure that we set the accelerator key marker and variables definitions
correctly::

  pofilter -t accelerators -t escapes -t variables -t xmltags --openoffice existing_files errors

Any messages that fail one of the 4 checks will be placed in files in *errors*.
We also used the :opt:`--openoffice` option to ensure that the tool is aware of
the OpenOffice.org accelerator marker (*~*) and the OpenOffice.org variable
styles (OpenOffice.org has over 10 variable styles).  You can also specify
other styles of project including GNOME, KDE or Mozilla.

You can also specify whether you want fuzzy entries included and checked, by
specifying the :opt:`--fuzzy` parameter. By default this is off because fuzzy
strings are usually known to be broken and will be reviewed by translators
anyway.

Similarly you can include items marked for review by specifying :opt:`--review`
or :opt:`--ingnorereview`.  By default review items are included.  This is not
part of the standard Gettext format. We have allowed entries like this when we
want to communicate to someone what error we have picked up::

  # (review) - wrong word for gallery chosen

You can run pofilter without the :opt:`-t` option.  This runs all the checks.
This can be confusing if you have a lot of errors as you easily lose focus.
One strategy is to run each test individually.  This allows you to focus on one
problem at a time across a number of files.  It is much easier to correct end
punctuation on its own then to correct many different types of errors.  For a
small file it is probably best to run all of the test together.

By using the :opt:`--autocorrect` option you can automatically correct some
very common errors.  Use with caution though. This option assumes you use the
same punctuation style as the source text.

.. _using_pofilter#edit_the_files:

Edit the files
--------------

Once the errors have been marked you can edit them with any text editor or PO
editor e.g. `Virtaal <http://virtaal.org>`_.  You will be editing the files in
the *errors* directory.  Only messages that failed one of the tests will be
present.  If no messages failed then there will be no error PO file for the
source PO file.  Only critical errors are marked fuzzy -- all others are simply
marked with the pofilter marker.  Critical errors are marked fuzzy as this
allows you to simply merge them back into you PO files and then rely on the
fact that all po2* tools will ignore a message marked fuzzy.  This allows you
to quickly eliminate messages that can break builds.

To edit run::

  vi `find errors -name "*.po"`
  virtaal `find errors -name "*.po"`

or similar command.

The pofilter marker helps you determine what error was discovered::

  # (pofilter) <test> - <explanation of test error>

Use the test description to help you determine what is wrong with the message.
Remember that all your changes will be ported back into the PO files.  So if
you leave a string fuzzy in the error files, it will become fuzzy in the main
files when you merge the corrected file back into the main file.  Therefore
delete anything you do not want to migrate back when you merge the files.
Delete the test comments and fuzzy markings as needed.  Leave them in if you
want another translator to see them.

The computer can get it wrong, so an error that pofilter finds may in fact not
be an error.  We'd like to hear about these false positives so that we can
improve the checks.  Also if you have some checks that you have added or ideas
for better checks, then let us know.

.. _using_pofilter#merging_your_corrections_back_into_the_originals:

Merging your corrections back into the originals
------------------------------------------------

After correcting the errors in the PO files its time to merge these corrections
back into the originals using :doc:`/commands/pomerge`. ::

  pomerge -t existing_files -i errors -o files_without_errors

If :opt:`-t` and :opt:`-o` are the same directory, the corrections will be
merged into the existing files.  Do this only if you are using some kind of
version control system so that you can check the changes made by
:doc:`/commands/pomerge`.

.. _using_pofilter#checking_the_corrections:

Checking the corrections
------------------------

We have done this against CVS but you could run a normal diff between a good
copy and your modifications.  Thus we assume in the last step that we merged
the corrections into the existing translations::

  pomerge -t existing_files -i errors -o existing_files

Now we check the changes using *cvs diff*::

  cvs diff -u existing_files > x.diff

This creates a unified diff (one with + and - lines so you can see what was
added and what was removed) in the file x.diff::

  vim x.diff

Check the diff file in any editor, here we use vim.  You should check to see
that the changes you requested are going in and that something major did not go
wrong.  Also look to see if you haven't left any lines with "# (pofilter): test
description" which should have been deleted from the error checking PO files.
Also check for stray fuzzy markers that shouldn't have been added.  You will
have to make corrections in the files in *existing_files* not in *errors*.

When you are happy that the changes are correct run::

  cvs ci existing_files

Congratulations you have helped eliminate a number of errors that could give
problems when running the application.  Now you might want to look at running
some of the other tests that check for style and uniformity in translation.
