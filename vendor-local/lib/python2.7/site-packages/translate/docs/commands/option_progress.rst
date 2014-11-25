
.. _option_progress:

--progress=PROGRESS
*******************

All of the programs can give visual feedback.  This options allows you to
select the style of that feedback.

In the examples we are converting and OpenOffice.org 2.0 sdf/gsi file into POT
files using :doc:`oo2po <oo2po>`.

.. _option_progress#none:

none
====

No visual feedback, this is useful if you want to use any of the scripts as
part of another script and don't want feedback to interfere with the operation.

.. code-block:: bash

    [dwayne@laptop OOo20]$ oo2po -P --progress=none en-US.sdf pot
    [dwayne@laptop OOo20]$

.. _option_progress#dots:

dots
====

Use visual dots to represent progress.  Each dot represent a file that has been
processed.

.. code-block:: bash

    [dwayne@laptop OOo20]$ oo2po -P --progress=dots en-US.sdf pot
    .............................................................................................
    .............................................................................................
    .........................................
    [dwayne@laptop OOo20]$

.. _option_progress#bar_default:

bar (default)
=============

Use a progress bar consisting of hashes (#) to show progress.

.. code-block:: bash

    [dwayne@laptop OOo20]$ oo2po -P --progress=bar en-US.sdf pot
    processing 227 files...
    [##############################             ]  69%

This is the default mode of operation, therefore this command would create the
same output.

.. code-block:: bash

    [dwayne@laptop OOo20]$ oo2po -P en-US.sdf pot

.. _option_progress#verbose:

verbose
=======

Combine the hash (#) progress bar form the *bar* option with the actual names
of files that have been processed.

.. code-block:: bash

    [dwayne@laptop OOo20]$ oo2po -P --progress=verbose en-US.sdf pot
    processing 227 files...
    so3/src.oo
    dbaccess/source/ui/uno.oo
    helpcontent2/source/text/shared.oo
    wizards/source/formwizard.oo
    sch/source/ui/dlg.oo
    helpcontent2/source/text/sbasic/shared/01.oo
    dbaccess/source/core/resource.oo
    svtools/source/sbx.oo
    dbaccess/source/ui/relationdesign.oo
    scp2/source/writer.oo
    filter/source/xsltdialog.oo
    [##                                         ]   5%

.. _option_progress#names:

names
=====

Prints out only the filenames without any other progress indicator.  This is a
good option when outputting to a log file rather than a terminal.

.. code-block:: bash

    [dwayne@laptop OOo20]$ oo2po -P --progress=names en-US.sdf pot
    so3/src.oo
    dbaccess/source/ui/uno.oo
    helpcontent2/source/text/shared.oo
    wizards/source/formwizard.oo
    sch/source/ui/dlg.oo
    helpcontent2/source/text/sbasic/shared/01.oo
    dbaccess/source/core/resource.oo
    svtools/source/sbx.oo
    dbaccess/source/ui/relationdesign.oo
    scp2/source/writer.oo
    filter/source/xsltdialog.oo

