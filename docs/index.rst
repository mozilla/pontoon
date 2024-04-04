Pontoon - Mozilla's Localization Platform
=========================================

`Pontoon <https://github.com/mozilla/pontoon>`_ is a translation management
system used and developed by the Mozilla localization community.
It can handle any project that uses one of the supported file formats:

- .dtd
- .ftl (Fluent)
- .inc
- .ini
- .json (WebExtensions)
- .json (key-value)
- .po (Gettext)
- .properties
- .xliff
- .xml (Android)

Pontoon can pull strings it needs to translate from an external source, and write
them back periodically. Typically these external sources are version control
repositories that store the strings for an application. Supported external
sources include **Git**, **Mercurial** and **Subversion**.

Other Documentation
-------------------

Important additional Pontoon documentation can also be found at the following sites:

`How to localize with Pontoon <https://mozilla-l10n.github.io/localizer-documentation/tools/pontoon/>`_ (Mozilla Localizer Documentation)

`How to manage localizations on Pontoon <https://mozilla-l10n.github.io/documentation/tools/pontoon>`_ (Mozilla Internal Tools Documentation)

(For an issue to improve the documentation, see  `#2214 <https://github.com/mozilla/pontoon/issues/2214>`_.)

Contributing
------------

If you are interested in contributing to Pontoon's code, start with
:doc:`dev/first-contribution`.

Deploying
---------

If you want to deploy your own instance of Pontoon, read the :doc:`admin/deployment`
section.

Once you have a running instance, you will likely want to learn about
:doc:`user/localizing-your-projects`, and then dive into
`management tasks <https://mozilla-l10n.github.io/documentation/tools/pontoon/>`_.

Localizing
----------

If you're looking for help on using Pontoon for localizing projects, whether on
Mozilla's instance or any other, you can read our
`How to use Pontoon <https://mozilla-l10n.github.io/localizer-documentation/tools/pontoon/>`_
documentation.

Contents
--------
.. toctree::
   :maxdepth: 2

   dev/first-contribution
   dev/setup
   dev/contributing
   admin/deployment
   admin/maintenance
   user/localizing-your-projects
   dev/setup-virtualenv
