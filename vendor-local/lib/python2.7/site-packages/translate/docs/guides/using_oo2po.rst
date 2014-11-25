
.. _using_oo2po:
.. _creating_openoffice.org_pot_files:

Creating OpenOffice.org POT files
*********************************

This quick start guide shows you how to create the PO Template files for your
OpenOffice.org translation.

.. _using_oo2po#quick_start:

Quick Start
===========

#. `Download the latest POT and GSI files
   <ftp://ftp.linux.cz/pub/localization/openoffice.org/devel/pot>`_
#. ``oo2po -P <gsi> <new-pots>``

.. _using_oo2po#detailed_description:

Detailed Description
====================

.. _using_oo2po#download_the_latest_pot_and_gsi_files:

Download the latest POT and GSI files
-------------------------------------

The POT files produced by Pavel Janik contain the associated en-US.sdf file
that you need to create your own languages SDF file.  This is the same file
that produces the POT files.  So to begin translating you don't need to go
further than this.

* `Download the latest POT and GSI files
  <ftp://ftp.linux.cz/pub/localization/openoffice.org/devel/pot>`_

However, you will need this file if you need to use some of the other features
of :doc:`/commands/oo2po` such as changing the source language from English.

.. _using_oo2po#produce_the_pot_files_using_oo2po:

Produce the POT files using oo2po
---------------------------------

::

  oo2po -P <gsi> <new-pots>
  oo2po -P en-US.gsi pot

This takes the *en-US.gsi* file and creates POT files in the *pot* directory.
The :opt:`-P` option ensures that .pot files are created instead of .po file.

If you want to create one large .pot file instead of a lot of small ones, you
should use the::

  oo2po -P --multifile=onefile en-US.gsi pot

option as described in :doc:`/commands/oo2po`.

.. _using_oo2po#produce_a_pot_files_with_french_source_text:

Produce a POT files with French source text
-------------------------------------------

You will need to have access to a French GSI file.  The following commands will
create a set of POT files with French as the source language::

  oo2po -P --source-language=fr fr.gsi pot-fr

This will take translations from *fr.gsi* and create a set of POT files in
*pot-fr*.  These POT files will have French as the source language.  You need
to make sure that fr.gsi is in fact up to date.
