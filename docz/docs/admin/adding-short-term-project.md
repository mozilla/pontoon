# Adding a Short-Term Project

Short-term projects are used for content that does not have a repository — newsletters, marketing campaigns, surveys, and similar one-off content. Strings are stored only in Pontoon's database.

## Process overview

The process mirrors creating a standard project, with two key differences:

- **Data Source** is set to `Database` instead of a VCS repository.
- You should **test on the staging server first** before creating on production.

## Step 1 — Create on staging

Access Pontoon's admin console on the **staging server** and click **ADD NEW PROJECT**.

| Field | Notes |
|---|---|
| **Name** | Name of the project (displayed in Pontoon's project selector). |
| **Slug** | Auto-generated from Name; used in URLs. |
| **Locales** | Select at least one locale. Use *copy supported locales from an existing project* to speed this up. |
| **Locales can opt-in** | Uncheck to prevent localizers from requesting this project. |
| **Data Source** | Select **Database**. |
| **Deadline** | Format: `YYYY-MM-DD`. |
| **Priority** | 1 (Lowest) to 5 (Highest). |

Click **SAVE PROJECT** and verify that the project behaves as expected on staging.

## Step 2 — Manage strings

Once the project is created, two string management links appear on the admin project page:

- **MANAGE STRINGS** — view, edit, add, and delete strings.
  - Click **NEW STRING** to add a string.
  - Click the trashcan icon to remove a string.
  - Edit the string content and comment inline.
  - Click **SAVE STRINGS** to commit changes.
- **DOWNLOAD STRINGS** — download current strings for local editing or archiving.

## Step 3 — Create on production

Once validated on staging, access the production admin console and recreate the project with the same settings. Select all supported locales. The new project immediately appears in the public project list after saving.

!!! note
    Unlike VCS-backed projects, short-term projects do not have a Sync process. String changes take effect immediately after saving.
