.. These notes are used in:
   1. Our email announcements
   2. The Translate Tools download page at toolkit.translatehouse.org
   3. Sourceforge download page in
      http://sourceforge.net/projects/translate/files/Translate%20Toolkit/1.12.0-rc1/README.rst/download

Translate Toolkit 1.12.0-rc1
****************************

*Not yet released*

This release contains many improvements and bug fixes. While it contains many
general improvements, it also specifically contains needed changes and
optimizations for the upcoming `Pootle <http://pootle.translatehouse.org/>`_
2.6.0 and `Virtaal <http://virtaal.translatehouse.org>`_ releases.

It is just over X months since the last release and there are many improvements
across the board.  A number of people contributed to this release and we've
tried to credit them wherever possible (sorry if somehow we missed you).

..
  This is used for the email and other release notifications
  Getting it and sharing it
  =========================
  * pip install translate-toolkit
  * `Sourceforge download
    <https://sourceforge.net/projects/translate/files/Translate%20Toolkit/1.12.0/>`_
  * Please share this URL http://toolkit.translatehouse.org/download.html if
    you'd like to tweet or post about the release.

Highlighted improvements
========================

Major changes
-------------

- Properties and DTD formats fix a number of issues
- Massive code cleanup looking forward Python 3 compatibility
- Important changes in development process to ease testing


Formats and Converters
----------------------

- Mozilla properties

  - The ``\uNN`` characters are now properly handled
  - Fixed conversion of successive Gaia plural units in prop2po

- DTD

  - Underscore character is now a valid character in entity names


General
-------

- Misc docs cleanups


...and loads of general code cleanups and of course many many bugfixes.


Contributors
------------

This release was made possible by the following people:

%CONTRIBUTORS%

And to all our bug finders and testers, a Very BIG Thank You.
