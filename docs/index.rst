Pontoon - Translate the Web. In Place.
======================================

Pontoon is a web interface for translating text into other languages. Pontoon
specializes in translating websites in-place, but can handle any project that
uses one of the file formats it supports:

- Gettext PO
- XLIFF
- FTL (L20n)
- Properties
- DTD
- INI
- INC
- .lang

Pontoon pulls strings it needs to translate from an external source, and writes
them back periodically. Typically these external sources are version control
repositories that store the strings for an application. Supported external
sources include:

- Git
- Mercurial
- Subversion

Contents
--------
.. toctree::
   :maxdepth: 2

   dev/install
   dev/install-docker
   dev/contributing
   dev/sync
   dev/api
   admin/deployment
   admin/maintenance
