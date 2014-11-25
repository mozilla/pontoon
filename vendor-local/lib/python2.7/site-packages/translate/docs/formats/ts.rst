
.. _ts:
.. _qt_linguist:

Qt .ts
******

The Qt toolkit uses a .ts file format to store translations which are
traditionally edited using Qt Linguist.

.. _ts#references:

References
==========

The format is XML and seems to only have been documented properly since Qt 4.3

* `Current DTD Specification
  <http://qt-project.org/doc/qt-5.0/qtlinguist/linguist-ts-file-format.html>`_ for Wt 5.0,
  older versions; `Qt 4.3
  <http://doc.qt.digia.com/4.3/linguist-ts-file-format.html>`_
* http://svn.ez.no/svn/ezcomponents/trunk/Translation/docs/linguist-format.txt

.. _ts#complete:

Complete
========

Note that :doc:`ts2po </commands/ts2po>` uses and older version and does not
support all of these features.  `Virtaal <http://virtaal.org>`_, `Pootle
<http://pootle.translatehouse.org>`_ and other users of the new ts class
support the following:

* Context
* Message: status (unfinished, finished, obsolete), source, translation,
  location
* Notes: comment, extracomment, translatorcomment (last two since Toolkit
  1.6.0)
* Plurals: numerusform

.. _ts#todo:

TODO
====

.. note:: A new parser has been added to the toolkit in v1.2. This allows
   `Virtaal <http://virtaal.org>`_, :doc:`/commands/pocount` and other users to
   work with v1.1 of the .ts format.  This corrects almost all of the issues
   listed below.  The converter :doc:`ts2po </commands/ts2po>` continues to use
   the older storage class and thus continue to experience some of these
   problems.

* Compliance with above DTD
* byte: within various text areas
* translation: obsolete (currently handled with comments in conversion to PO.
  But should be able to convert Obsolete PO back into obsolete TS.  This might
  mean moving this format properly onto the base class).
* lengthvariants
* \*comment: various new comment fields
* old\*: ability to store previous source and comments

.. _ts#validate:

Validate
========

These might work but need validation

* Encoding handling for non-UTF-8 file encodings
