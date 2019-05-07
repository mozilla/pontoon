Set up your first Project
=========================

Make your project localizable
-----------------------------
Project owners can follow these guidelines to properly structure files inside the repository.

1. Ensure that your project works with one of the `supported l10n frameworks`_.
2. Extract localizable strings into resource files.
3. Put all individual locale folders at the same nesting level of a dedicated `locales` folder.
4. Source locale needs to be called `templates`, `en-US`, `en-us` or `en`. In case of multiple
   folders with such name, the first one will be used.
5. Locale code must not be part of the file name.

   Correct pattern::

       locales/{locale_code}/path/to/file.extension

   Incorrect pattern::

       locales/{locale_code}/path/to/file.{locale_code}.extension

.. _supported l10n frameworks: ../index.html/

Alternatively, you can add a `project config file`_ to define the path of resource files and locale folders.

.. _project config file: https://moz-l10n-config.readthedocs.io/en/latest/fileformat.html

At last, if you want to use SSH for working with GitHub (recommended), you'll need to add
your-pontoon-instance-github-bot (like `mozilla-pontoon`_ ) as a collaborator to your repository.

.. _mozilla-pontoon: https://github.com/mozilla-pontoon/

Create the project in your Pontoon instance
-------------------------------------------
When accessing your freshly deployed app, your email address is your login in the Sign In page
and your password is the one picked during the setup phase.

Access Pontoon’s admin console (`/admin`) on the stage server and click ADD NEW PROJECT.

* Name: name of the project to be displayed in Pontoon’s project selector.
* Slug: used in URLs, will be generated automatically based on the project’s name.
* Locales:
    * Localizable: at least one locale needs to be selected. You can also copy supported locales
      from an existing project.
    * Read-only: add locale in read-only mode. In this way, their translations will be available
      to other languages in the LOCALES tab when translating, but it won’t be possible to change
      or submit translations directly in Pontoon.
    * Locales can opt-in checkbox: uncheck it to prevent localizers from requesting this specific project.
* Data Source: select ``repository`` if the project is located in a GIT/HG/SVN repository, otherwise,
  select ``database`` if you want to keep the project stored only in Pontoon’s database.
* Repositories: enter your repository ``SSH URL`` and set your working branch to commit translations
  in a branch instead of master.
* Download prefix: a URL prefix for downloading localized files. For GitHub repositories, select
  any localized file on GitHub, click Raw and replace locale code and the following bits in the
  URL with {locale_code}. For example, if the link is
  `https://raw.githubusercontent.com/mozilla/addons-server/master/locale/sq/LC_MESSAGES/djangojs.po`,
  the field should be set to `https://github.com/mozilla/addons-server/blob/master/locale/{locale_code}`

Additionally, you can add a description, set the translation priority and enable tags.
Please refer to the `new project documentation`_ for complete description.

.. _new project documentation: https://mozilla-l10n.github.io/documentation/tools/pontoon/adding_new_project.html

Click SAVE PROJECT at the bottom of the page, then click SYNC to run a test sync. In the
Sync log (`/sync/log/`) you should be able to see if it succeeded or failed.
