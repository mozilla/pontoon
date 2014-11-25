
.. _ical:
.. _icalendar:

iCalendar
*********

Support for :wp:`iCalendar <ICalendar>` (\*.ics) files.  This allows calendars
to be localised.

The format extracts certain properties from VEVENT objects.  The properties are
limited to textual entries that would need to be localised, it does not include
entries such as dates and durations that would indeed change for various
locales.

.. _ical#resources:

Resources
=========

* `rfc2445 <http://tools.ietf.org/html/rfc2445>`_ -- Internet Calendaring and
  Scheduling Core Object Specification (iCalendar)
* iCal `spec <http://www.kanzaki.com/docs/ical/>`_ in a simple adaptation of
  the rfc that makes it easy to refer to all sections, items and attributes.
* `VObject <http://vobject.skyhouseconsulting.com/>`_ -- the python library
  used to read the iCal file.
* `iCalender validator <http://severinghaus.org/projects/icv/>`_
* :wp:`iCalendar <ICalendar>`
* `Components and their properties
  <https://upload.wikimedia.org/wikipedia/commons/c/c0/ICalendarSpecification.png>`_

.. _ical#conformance:

Conformance
===========

We are not creating iCal files, simply extracting localisable information and
rebuilding the file.  We rely on VObject to ensure correctness.

The following data is extracted:

* VEVENT:

  * SUMMARY
  * DESCRIPTION
  * LOCATION
  * COMMENTS

No other sections are extracted.

.. _ical#notes:

Notes
=====

.. _ical#language:_not_a_multilingual_solution:

LANGUAGE: not a multilingual solution
-------------------------------------

It is possible to set the language attribute on an entry e.g.::

  SUMMARY:LANGUAGE=af;New Year's Day

However since only one SUMMARY entry is allowed this does not allow you to
specify multiple entries which would allow a single multilingual file.  With
that in mind it is not clear why the LANGUAGE attribute is allowed, the
examples they give are for LOCATION entries but that is still not clearly
useful.

.. _ical#broken_lotus_notes:

Broken Lotus Notes
------------------

Lotus notes creates broken iCalendar files.  They include _ (underscore) in
some of the property names, while [A-Z0-9\\-] are the only valid chars.
Therefore, we require vobject >= v0.6.5 (but there is unfortunately no way to
check for the version of vobject).  See `vobject bug 12008
<https://bugzilla.osafoundation.org/show_bug.cgi?id=12008>`_ for further
details.

.. _ical#development_notes:

Development Notes
=================

If we use LANGUAGE at all it will be to ensure that we specify that an entry is
in a given language.
