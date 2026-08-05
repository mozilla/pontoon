- Feature Name: Community health score (CHS) panel
- Created: 2026-08-04
- Associated PR: [#4189](https://github.com/mozilla/pontoon/pull/4189)

# Summary

Introduce an admin-only Community health score panel within the global Insights dashboard that provides a monthly breakdown of the Community health score and its underlying metrics, along with historical score tracking. Also make the historical tracking available on locale Insights dashboards.

# Motivation

Currently, the Community health score is calculated via a series of moz-l10n scripts and Google Sheets formulas, collected manually on a monthly basis. Other than the tedious nature of needing to do this manually, PMs need better options to analyze CHS data holistically.

# Feature explanation

## Community health score aggregation

On the first of each month, an automation is run that collects telemetry on the state of each locale for the **previous month**. The data collected for **each locale** is compiled into the following datapoints:
- `active_managers`: managers with **reviews performed** + **approved translations** > 500 in the past 12 months
- `active_translators` translators with **reviews performed** + **approved translations** > 400 in the past 12 months
- `active_contributors` contributors with **approved translations** > 200 in the past 12 months
- `all_contributors` contributors with **approved translations** + **rejected translations** + **pending suggestions** > 200 in the past 12 months
- `new_signups` new signups with **approved translations** > 100 in the past 12 months
- `key_projects_enabled` number of projects that are classified as key projects via the `is_chs_project` flag
- `completion` locale completion as a function of **approved_strings** + **strings_with_warnings** / **total strings**

The data used is then computed into the following scores based on predetermined thresholds:

- `active_managers_score`: score representation of `active_managers`
- `active_translators_score` score representation of `active_translators`
- `active_contributors_score` score representation of `active_contributors`
- `all_contributors_score` score representation of `all_contributors`
- `new_signups_score` score representation of `new_signups`
- `key_projects_enabled_score` score representation of `key_projects_enabled`
- `completion_score` score representation of `completion`

Finally the scores are combined into a **Community health score** for that locale on that month, which is used for measuring locale health.

## Community health score panel

The new "Community health score" panel located at `/insights` consists of a table of locales similar to the `/teams` page, and a graph.

Table:

Widget: contains locale search and buttons titled `Edit Locales` and `Show Scores`
  - `Edit Locales`: links to a selector that enables admins to change locale availability on the CHS panel
  - `Show Scores`: toggles default and score view of components that make up the CHS

Each row contains the following information:
  - **Locale code** linking to individual locale pages
  - Number of **active managers**
  - Number of **active translators**
  - Number of **active contributors**
  - Number of **all contributors**
  - Number of **new signups**
  - Number of **enabled key projects** (&)
  - Overall locale **completion** (%)
  - CHS, written as a float


Beside each statistic, an up/down arrow combined with a smaller number, indicating increase or decrease, presents the delta over the previous month's statistic. Data that has no change is not represented with a delta. For counts (contributor, translator, manager counts etc.), each value is represented as an integer. For the scores and percentages, each value is represented with 2 places.
- Graph:
  - Tooltip: describes basic functionality, which is to track CHS per locale
  - Legend: contains locales and `Average (all locales)`, which can be selected/deselected to display corresponding CHS datapoints over time.
  - Display: displays CHS scores for selected locales trailing 12 months. As soon as the CHS calculation automation on Pontoon runs on the first of each month, the previous month's scores will be automatically available for display.

## Insights Configuration

The CHS panel has a button named `Edit Locales`. Upon clicking it, admins are redirected to a locale selector that enables them to add/remove locales from their view.

## Locale Insights changes

The `/<locale-code>/insights/` page currently includes statistics and useful information regarding locale health and performance. The main change includes a new graph as follows:

- Graph:
  - Name: `Community health score`
  - Tooltip: describes basic functionality, which is to track CHS of current locale
  - Display: displays CHS scores for current locale trailing 12 months. As soon as the CHS calculation automation on Pontoon runs on the first of each month, the previous month's scores will be automatically available for display.
