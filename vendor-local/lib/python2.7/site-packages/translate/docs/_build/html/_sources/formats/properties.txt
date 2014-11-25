
.. _properties:

Mozilla and Java properties files
*********************************

The Translate Toolkit can manage Java .properties files with the
:doc:`/commands/prop2po` and po2prop tool. As part of the Mozilla localisation
process, the :doc:`/commands/moz2po` tool handles the properties files along
with the other files. The tools can also handle Skype .lang files. Some related
formats with their own documentation:

* :doc:`Mac OSX strings <strings>`
* :doc:`Adobe Flex <flex>` properties files.

.. _properties#features:

Features
========

* Fully manage Java escaping (Mozilla non-escaped form is also handled)
* Preserves the layout of the original source file in the translated version

.. versionadded:: 1.12.0

* Mozilla accelerators -- if a unit has an associated access key entry then
  these are combined into a single unit

.. _properties#not_implemented:

Not implemented
===============

* We don't allow filtering of unchanged values.  In Java you can inherit
  translations, if the key is missing from a file then Java will look to other
  files in the hierarchy to determine the translation.

.. _properties#examples:

Examples
========

.. code-block:: properties

  editmenu.label = "Edit"
  saveas.label = "Save As"

.. _properties#references:

References
==========

- Java Properties Class's `load()
  <http://docs.oracle.com/javase/1.5.0/docs/api/java/util/Properties.html#load(java.io.InputStream)>`_
  describes the properties format.
- http://www.oracle.com/webfolder/technetwork/jsc/dtd/properties.dtd --
  alternate XML based property representation
