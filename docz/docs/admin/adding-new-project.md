# Adding a New Project

This page explains how to add a standard VCS-backed project to Pontoon. For database-backed short-term projects (newsletters, campaigns, etc.), see [Adding a Short-Term Project](adding-short-term-project.md).

## Prerequisites

Before adding a project to Pontoon, ensure that:

1. The project uses a [supported localization file format](../dev/localizing-your-projects.md#supported-file-formats).
2. Localizable strings are extracted into resource files and pushed to a GitHub (or Mercurial) repository.
3. Pontoon has **write access** to the repository — the recommended approach is to create a dedicated GitHub account for your Pontoon instance, add it as a collaborator to the repository, and configure `SSH_KEY` and `SSH_CONFIG` in your deployment.

Check the repository structure against [Pontoon's requirements](../dev/localizing-your-projects.md#repository-structure). Review files for localization quality issues: unclear strings, missing localization comments, missing plural forms.

## Creating the project

Access Pontoon's admin console at `/admin/` and click **ADD NEW PROJECT**.

### Required fields

| Field | Notes |
|---|---|
| **Name** | Displayed throughout Pontoon. Reserved names: *Terminology*, *Tutorial*, *Pontoon Intro*. |
| **Slug** | Used in URLs; auto-generated from Name. |
| **Locales** | Select at least one localizable locale by clicking on it. |
| **Repository URL** | Use the SSH URL: `git@github.com:user/repo.git`. |

### Optional fields

| Field | Notes |
|---|---|
| **Branch** | Leave empty to use the default branch (usually `main` or `master`). |
| **Public Repository Website** | Displayed on dashboards. Pontoon attempts to prefill this from the Repository URL. |
| **Download prefix or path to TOML file** | A URL prefix for downloading localized files. |
| **Visibility** | `private` (default) — admins only; `public` — visible to all. |
| **Project info** | Context or testing instructions for localizers. HTML supported. |
| **Internal admin notes** | For developer contacts and PM handoff notes; not visible to localizers. |
| **Deadline** | Format: `YYYY-MM-DD`. |
| **Priority** | 1 (Lowest) to 5 (Highest). |
| **Contact** | The L10n driver responsible for this project. |
| **External Resources** | Links to preview environments, screenshots, etc. |
| **Pretranslation** | See [Managing Pretranslation](managing-pretranslation.md). |
| **Locales can opt-in** | Uncheck to prevent localizers from requesting this project. |
| **Tags enabled** | Check to allow resource grouping by tag. |
| **Read-only** | Column in the Locales section; marks a locale as read-only. |

## First sync

1. Click **SAVE PROJECT** at the bottom of the page.
2. Click **SYNC** to run a test sync.
3. Monitor progress in the **Sync log** at `/sync/log/`.
4. Verify that imported resources and strings look correct.

!!! important
    The new project only appears in the public project list after the next sync cycle AND after you set **Visibility** to `Public`.

## Tags

Tags logically group resources and can be assigned a priority. To use tags:

1. Check **Tags enabled** and save the project.
2. After saving, a tag management section appears — create tags and save again.
3. Associate resources with tags via the resource section of the admin panel.
4. It's also possible to set a **deadline** per Resource (not just per project) from the resource section.

## Read-only locales

In the Locales table, the **Read-only** column marks a locale's translations as visible but not editable in Pontoon. Other locales can reference these translations in the LOCALES tab.
