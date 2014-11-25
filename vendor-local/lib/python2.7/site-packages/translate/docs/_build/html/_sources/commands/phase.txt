
.. _phase:

phase
*****

phase is a script that allows you to perform a number of tasks on a set of PO
files that have been broken into phases.  You can create a ZIP file for a
phase, run checks against a phase, review a phase, edit files in a phase, etc.
All the tasks that would be involved in sending work to various translators,
receiving work, checking it and committing to CVS.

.. _phase#prerequisites:

Prerequisites
=============

* An environment that will run :man:`bash`
* :man:`diff`
* :man:`cvs`

.. _phase#latest_version:

Latest Version
==============

phase is not currently distributed as part of the toolkit.  You can get the
`latest version from Git
<https://raw.github.com/translate/translate/master/tools/phase>`_

.. _phase#usage:

Usage
=====

::

  phase <command> [options]

Mostly the usage follows the format of::

  phase <command> <language-dir> <phaselist> <phase-name>
  phase <command> <language-dir> <phase-name>

A full list of commands and options can be seen by running::

  phase --help

.. _phase#commands:

Commands
========

These are the commands that you can use:

* makephaselist <new-phase-list-name> -- creates a phase list
* listphases <phase-list> -- lists the different phases that appear in the
  phase-list file
* listfiles <phase-list> <phase-name> -- list all files for the given phase in
  the phase-list file
* checkphaselist <language-dir> <phase-list> -- checks to see which files are
  not included in the phaselist
* countpo <language-dir> <phase-list> <phase-name> -- counts PO file in the
  given phase
* countpot <template-dir> <phase-list> <phase-name> -- counts POT file in the
  given phase
* missingpo <language-dir> <phase-list> <phase-name> -- lists files that have
  not been returned for a phase
* packpot <template-dir> <phase-list> <phase-name> -- packs all POT files for a
  given phase into a ZIP file
* packpo <language-dir> <phase-list> <phase-name> -- packs all PO files for a
  given phase into a ZIP file
* packall <template-dir> <phase-list> -- packs all phases found in the phase
  list
* packallpo <language-dir> <phase-list> -- packs all phases found in the phase
  list for the given language
* countmismatch <language-dir> <template-dir> <phase-list> <phase-name> --
  compares the source word count between PO and POT to determine if there are
  any file errors.
* editpo <language-dir> <phase-list> <phase-name> -- edit the PO files in a
  phase
* editpochecks <language> <phase-name> -- edit the PO checks output by checkpo
* editconflicts <language-dir> <phase-list> <phase-name> -- edit the extracted
  conflict items
* checkpo <language-dir> <phase-list> <phase-name> [pofilter options] -- run
  pofilter checks against the given phase
* mergepo <language> <phase-name> -- merge the checks back into the main
  language directory
* conflictpo <language-dir> <phase-list> <phase-name> [poconflict options] --
  run poconflict checks against the given phase
* diffpo <language-dir> <phase-list> <phase-name> -- perform a cvs diff for the
  phase
* cvslog <language-dir> <phase-list> <phase-name> -- perform a cvs log against
  files in the phase
* lastlog <language-dir> <phase-list> <phase-name> -- retrieves the last cvs
  log entry for each file in a phase
* cvsadd <languages-dir> <phase-list> <phase-name> -- CVS adds files and
  directories that are not already in CVS
* diffpo <language-dir> <phase-list> <phase-name> -- perform a cvs diff for the
  phase
* reviewpo <language-dir> <phase-list> <phase-name> [pofilter options] --
  extract items marked for review for the given phase
* editreviews <language-dir> <phase-list> <phase-name> -- edit the extracted
  review items
* countreviews <language-dir> <phase-list> <phase-name> -- count the number of
  strings and words under review
* checkinpo <language-dir> <phase-list> <phase-name> -- cvs checkin the files
  in the given phase
* creategsi <language-dir> <en-US.gsi> <traget-language> -- creates a BZ2
  GSI/SDF file for the language against the en-US GSI file
* reviewsinout <language> <phase-name> -- counts the number of review files
  returned vs sent and shows which are missing
* reviewsdiff <language> <phase-name> -- create a diff between what was sent
  for review and what was returned

.. _phase#bugs:

Bugs
====

There are probably lots mostly the bug is that the command line options are
pretty inconsistent
