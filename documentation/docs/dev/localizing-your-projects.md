---
title: Localizing your projects
---

The following describes how to make your projects localizable with your
Pontoon instance.

Pontoon specializes in using version control systems as the source and
store of localizable strings. While internal Pontoon DB can be used for
that purpose as well, steps below assume you store strings in a [GitHub
repository](https://help.github.com/en/articles/create-a-repo).

# Prerequisites

Before you can set up a new project in Pontoon:

1.  Ensure your project works with one of the
    `supported l10n frameworks <../index>`{.interpreted-text
    role="doc"}.

2.  Extract localizable strings into resource files.

3.  Push resource files to your GitHub repository.

4.  Make sure your Pontoon instance has write access to your repository.

    ::: note
    ::: title
    Note
    :::

    The recommended way for that is to create a dedicated GitHub account
    for your Pontoon instance, [add it as a
    collaborator](https://help.github.com/en/articles/inviting-collaborators-to-a-personal-repository)
    to your repository, and set `SSH_KEY` and `SSH_CONFIG`
    `as documented <../admin/deployment>`{.interpreted-text role="doc"}.
    :::

# Folder structure

To let Pontoon discover your localizable files, you\'ll either need to
specify paths in the [project configuration
file](https://moz-l10n-config.readthedocs.io/en/latest/fileformat.html)
or strictly follow the file and folder structure as expected by Pontoon:

1.  Locale folders (including source locale) must be located at the same
    nesting level of the directory tree. You may want to put all locale
    folders under a `locales` folder.
2.  Source locale needs to be called `templates`, `en-US`, `en-us` or
    `en`. If multiple folders with such name exist in the repository and
    contain files in a supported file format, the first one will be
    used.
3.  Locale folder names must always match locale identifiers used by
    Pontoon. If your application requires different identifiers, you can
    try creating symbolic links to locale folders.
4.  Locale code must not be part of the file name.

Correct pattern:

    locales/{locale_code}/path/to/file.extension

Incorrect pattern:

    locales/{locale_code}/path/to/file.{locale_code}.extension

For Gettext files, you will need to ensure that `.po` files are included
in the repository for each target locale for which they are to be
translated (these files may be initially empty). For all other supported
formats, Pontoon will automatically add files for each locale when it is
translated.

# Adding a new project to Pontoon

When accessing your deployed app, your email address is your login in
the Sign In page and your password is the one picked during setup. After
you log in, access Pontoon Admin (`/admin/`), click **ADD NEW PROJECT**
and fill out the following required fields:

1.  **Name**: name of the project to be displayed throughout Pontoon
    app. The following project names are reserved: `Terminology`,
    `Tutorial`, `Pontoon Intro`.
2.  **Slug**: used in URLs, will be generated automatically based on the
    Name.
3.  **Locales**: select at least one Localizable locale by clicking on
    it.
4.  **Repository URL**: enter your repository\'s SSH URL of the form
    `git@github.com:user/repo.git`.
5.  **Download prefix or path to TOML file**: a URL prefix for
    downloading localized files.
6.  Click **SAVE PROJECT** at the bottom of the page.
7.  After the page reloads, click **SYNC** and wait for Pontoon to
    import strings. You can monitor the progress in the Sync log
    (`/sync/log/`).
8.  When the synchronization is finished, you should check the imported
    resources and the entities. If everything went okay, you can proceed
    to the next step.
9.  Go to the project\'s admin page and change the visibility option to
    make the project public. It\'s required because all new projects in
    Pontoon are private by default and aren\'t visible to localizers and
    locale managers.

For complete documentation of the Admin form, please refer to Mozilla\'s
[new project
documentation](https://mozilla-l10n.github.io/documentation/tools/pontoon/adding_new_project.html).

At this point you are ready to [start localizing your
project](https://mozilla-l10n.github.io/localizer-documentation/tools/pontoon/)
at `/projects/SLUG/`!
