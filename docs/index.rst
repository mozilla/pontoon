Pontoon - Mozilla's Localization Platform
=========================================

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

Pontoon can pull strings it needs to translate from an external source, and write
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

   dev/setup
   dev/contributing
   dev/browser-support
   admin/deployment
   admin/maintenance
   dev/setup-virtualenv
