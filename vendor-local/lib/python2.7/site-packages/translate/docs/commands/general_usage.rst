
.. _general_usage:

General Usage
*************

The tools follow a general usage convention which is helpful to understand.

.. _general_usage#input_&_output:

Input & Output
==============

The last two arguments of your command are the input and output
files/directories::

  moz2po <input> <output>

You can of course still us the :opt:`-i` and :opt:`-o` options which allows you
to reorder commands ::

  moz2po -o <output> -i <input>

.. _general_usage#error_reporting:

Error Reporting
===============

All tools accept the option :opt:`--errorlevel`.  If you find a bug, add this
option and send the traceback to the developers. ::

  moz2po <other-options> --errorlevel=traceback

.. _general_usage#templates:

Templates
=========

If you are working with any file format and you wish to preserve comments and
layout then use your source file as a template. ::

  po2dtd -t <source-file> <input> <output>

This will use the files in ``<source-file>`` as a template, merge the PO files
in ``<input>``, and create new DTD files in ``<output>``

If you ran this without the templates you would get valid DTD files but they
would not preserve the layout or all the comments from the source DTD file

The same concept of templates is also used when you merge files. ::

  pomerge -t <old> <fixes> <new>

This would take the ``<old>`` files merge in the ``<fixes>`` and output new PO
files, preserving formatting, into ``<new>``.  You can use the same directory
for ``<old>`` and ``<new>`` if you want the merges to overwrite files in
``<old>``.

.. _general_usage#source2target:

source2target
=============

The converters all follow this convention:

* source = the format from which you are converting e.g. in :doc:`oo2po
  <oo2po>` we are converting from OpenOffice.org SDF/GSI
* target = the format into which you are converting e.g. in :doc:`oo2po
  <oo2po>` we are converting to Gettext PO

.. _general_usage#getting_help:

Getting Help
============

The :opt:`--help` option will always list the available commands for the tool. ::

  moz2po --help
