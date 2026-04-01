# Admin Guide

This guide covers administrative tasks in Pontoon — managing projects, locales, users, and communication tools.

!!! note
    The screenshots in this documentation use the dark theme, but a light theme is also available in your [profile settings](../localizer/users.md).

## Sections

<div class="grid cards" markdown>

- :material-folder-plus: **[Adding a New Project](adding-new-project.md)**

    How to set up a standard VCS-backed project in Pontoon, including repository configuration, locale selection, tags, and deadlines.

- :material-calendar-clock: **[Adding a Short-Term Project](adding-short-term-project.md)**

    How to create database-backed projects for newsletters, campaigns, and surveys — no VCS required.

- :material-translate: **[Adding a New Locale](adding-new-locale.md)**

    How to add a new language/locale to Pontoon, including machine translation setup and plural rules.

- :material-robot: **[Managing Pretranslation](managing-pretranslation.md)**

    How to enable automated pretranslation for a project and train custom Google AutoML models.

- :material-message-text: **[Messaging Center](messaging-center.md)**

    How to send targeted emails and in-app notifications to contributors.

- :material-file-edit: **[Renaming a Localization File](renaming-file.md)**

    Steps to rename a resource file without losing translation history.

- :material-pencil: **[Renaming a Project](renaming-project.md)**

    Steps to safely rename a project slug and update references.

- :material-account-multiple: **[Managing Users](managing-users.md)**

    How to deactivate or remove user accounts.

- :material-book-alphabet: **[Adding Terminology](adding-terminology.md)**

    How to add terms to the Pontoon glossary/terminology project.

</div>

## Accessing the admin console

The Pontoon admin console is available at `/admin/` (e.g., `pontoon.mozilla.org/admin/`). Django's standard admin interface is at `/a/`.

!!! info
    Only Administrators have access to the admin console. Changes made here affect all users and projects.
