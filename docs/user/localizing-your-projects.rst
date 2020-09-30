Localizing your projects
========================

The following describes how to make your projects localizable with your Pontoon
instance.

Pontoon specializes in using version control systems as the source and store of
localizable strings. While internal Pontoon DB can be used for that purpose as
well, steps below assume you store strings in a `GitHub repository`_.

Prerequisites
-------------
Before you can set up a new project in Pontoon:

#. Ensure your project works with one of the :doc:`supported l10n frameworks <../index>`.
#. Extract localizable strings into resource files.
#. Push resource files to your GitHub repository.
#. Make sure your Pontoon instance has write access to your repository.

   .. Note::

        The recommended way for that is to create a dedicated GitHub account
        for your Pontoon instance, `add it as a collaborator`_ to your
        repository, and set ``SSH_KEY`` and ``SSH_CONFIG`` :doc:`as documented <../admin/deployment>`.

.. _GitHub repository: https://help.github.com/en/articles/create-a-repo
.. _add it as a collaborator: https://help.github.com/en/articles/inviting-collaborators-to-a-personal-repository

Folder structure
----------------

To let Pontoon discover your localizable files, you'll either need to specify
paths in the `project configuration file`_ or strictly follow the file and folder
structure as expected by Pontoon:

#. Locale folders (including source locale) must be located at the same nesting
   level of the directory tree. You may want to put all locale folders under a
   ``locales`` folder.
#. Source locale needs to be called ``templates``, ``en-US``, ``en-us`` or
   ``en``. If multiple folders with such name exist in the repository and
   contain files in a supported file format, the first one will be used.
#. Locale folder names must always match locale identifiers used by Pontoon.
   If your application requires different identifiers, you can try creating
   symbolic links to locale folders.
#. Locale code must not be part of the file name.

Correct pattern::

    locales/{locale_code}/path/to/file.extension

Incorrect pattern::

    locales/{locale_code}/path/to/file.{locale_code}.extension

.. _project configuration file: https://moz-l10n-config.readthedocs.io/en/latest/fileformat.html

Adding a new project to Pontoon
-------------------------------
When accessing your deployed app, your email address is your login in the Sign
In page and your password is the one picked during setup. After you log in,
access Pontoon Admin (``/admin/``), click **ADD NEW PROJECT** and fill out the
following required fields:

#. **Name**: name of the project to be displayed throughout Pontoon app. The
   following project names are reserved: ``Terminology``, ``Tutorial``,
   ``Pontoon Intro``.
#. **Slug**: used in URLs, will be generated automatically based on the Name.
#. **Locales**: select at least one Localizable locale by clicking on it.
#. **Repository URL**: enter your repository's SSH URL of the form
   ``git@github.com:user/repo.git``.
#. **Download prefix or path to TOML file**: a URL prefix for downloading localized files. For
   GitHub repositories, select any localized file on GitHub, click ``Raw`` and
   replace locale code and the following bits in the URL with ``{locale_code}``.
   If you use one, you need to select the `project configuration file`_ instead
   of a localized file.
#. Click **SAVE PROJECT** at the bottom of the page.
#. After the page reloads, click **SYNC** and wait for Pontoon to import
   strings. You can monitor the progress in the Sync log (``/sync/log/``).
#. When the synchronization is finished, you should check the imported resources
   and the entities. If everything went okay, you can proceed to the next step.
#. Go to the project's admin page and change the visibility option to make
   the project public. It's required because all new projects in Pontoon are private
   by default and aren't visible to localizers and locale managers.

For complete documentation of the Admin form, please refer to Mozilla's
`new project documentation`_.

At this point you are ready to `start localizing your project`_ at
``/projects/SLUG/``!

.. _new project documentation: https://mozilla-l10n.github.io/documentation/tools/pontoon/adding_new_project.html
.. _start localizing your project: https://mozilla-l10n.github.io/localizer-documentation/tools/pontoon/
