
.. _rc:
.. _windows_rc:

Windows RC files
****************

.. versionadded:: 1.2

Windows .rc files, or resource files, are used to store translatable text,
dialogs, menu, etc. for Windows applications.  The format can be handled by the
Translate Toolkit :doc:`/commands/rc2po` and po2rc.

.. _rc#conformance:

Conformance
===========

The actual specification of .rc files is hard to come by.  The parser was built
using :wp:`WINE <Wine_%28software%29>` .rc files as a reference.  This was done
as WINE is a good target for .rc translations.  We are confident though that
the extraction will prove robust for all .rc files.

.. _rc#useful_resource:

Useful resource
===============

* `RC converter <http://www.soft-gems.net:8080/browse/RC-Converter>`_
* `ReactOS translation instructions
  <http://www.reactos.org/wiki/index.php/Translating_introduction>`_

.. _rc#supported_elements:

Supported elements
==================

* DIALOG, DIALOGEX: All translatables
* MENU: POPUP, MENUITEM
* STRINGTABLE
* LANGUAGE: We only parse the first language tag, further LANGUAGE section are
  ignored

.. _rc#bugs:

Bugs
====

* There may be problems with very deeply nested MENU's
* LANGUAGE elements cannot yet be updated in :doc:`po2rc </commands/rc2po>`
  (:issue:`Issue 360 <360>`)

