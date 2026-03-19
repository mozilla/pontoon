# Team & Project Pages

Pontoon organizes work around **Teams** (one per locale) and **Projects** (one per product or website). This page explains how to navigate these pages and what you can do from each.

## Projects page

The Projects page lists all projects available in Pontoon. Access it by clicking **Projects** in the page header or navigating to `/projects`.

Each project entry shows:

- **Priority** (1–5 stars), based on product importance, user base size, and update frequency.
- **Target date** (for projects with a deadline).
- **Repository** link.
- **External resources** (e.g., testing instructions, screenshots).

A blue lightbulb icon in the rightmost column indicates the project has unreviewed translations. Click the lightbulb icon in the column header to sort by unreviewed count.

## Project page

Clicking a project opens its Project page. The header shows the project manager, overall completion status, and statistics across all enabled locales.

Tabs available on the Project page:

| Tab | Description |
|---|---|
| **Teams** | All locales enabled for this project. Clicking a locale opens the Localization page. |
| **Tags** | Logical groups of resources (visible only if tags are enabled). |
| **Contributors** | Active contributors and their statistics, filterable by time period. |
| **Insights** | Charts showing translation completion trends, human vs. machinery translations, active users, and time-to-review metrics. |
| **Info** | Project description and context. |

### Requesting a new language for a project

From the Project page, click **REQUEST NEW LANGUAGE**, select the locale, and click **REQUEST NEW LANGUAGE** again. An email is sent to Pontoon administrators; the Project Manager acts on the request.

!!! note
    Some projects have a closed list of supported locales and cannot be requested.

## Team page

Each locale has a Team page (e.g., `pontoon.mozilla.org/fr/`). The header shows the team's overall completion and statistics.

Tabs available on the Team page:

| Tab | Description |
|---|---|
| **Projects** | All projects enabled for this locale. |
| **Contributors** | Active contributors and their statistics, filterable by time period. |
| **Insights** | Trends for translation activity, active users, and review time. |
| **Bugs** | Open Bugzilla bugs for the locale (Mozilla deployment only). |
| **Info** | Team description; editable by Team Managers. |
| **Permissions** | User permissions panel (Team Managers and Admins only). |
| **TM** | Translation memory management (Translators and Team Managers). |

### Team Insights

The **Insights** tab on the Team page shows:

- **Translation activity** — completion percentage trend, with human vs. machinery translation bars per month.
- **New source strings** — toggle to show/hide.
- **Active users** — ratio of active vs. total users per role (managers, reviewers, contributors), filterable by time period.
- **Time to review suggestions** — average age of reviewed suggestions per month, with a 12-month rolling average.

### Requesting more projects for a locale

From the Team page, click **REQUEST MORE PROJECTS**, select the projects, and click **REQUEST NEW PROJECT**. This requests that an existing Pontoon project be enabled for your locale — it cannot be used to request a brand new project.

### Requesting pretranslation

From the Team page, click **REQUEST PRETRANSLATION**, select the projects, and click **REQUEST PRETRANSLATION**. Administrators will evaluate the request.

### Translation memory management

Team Managers and Translators can manage the team's TM from the **TM** tab:

- View all TM entries (source string + translation), searchable by source string or translation.
- Click a TM entry to open the corresponding string in the translation workspace.
- **Edit** a TM entry by clicking the Edit button in the Actions column, modifying the text, and clicking Save.
- **Upload** a TMX file using the upload control. Import progress is shown, and a success or error message appears when complete.

## Localization page

The Localization page shows project-specific information for a single locale. Access it by:

- Selecting a locale from a Project page.
- Selecting a project from a Team page.

Tabs on the Localization page:

| Tab | Description |
|---|---|
| **Resources** | Files available in this project for the locale. |
| **Tags** | Tag groups (if enabled for the project). |
| **Contributors** | Contributors to this locale+project combination, filterable by time. |
| **Insights** | Localization-specific trends. |
