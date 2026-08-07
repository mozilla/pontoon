- Feature Name: Community health score (CHS) panel
- Created: 2026-08-04
- Associated PR: [#4189](https://github.com/mozilla/pontoon/pull/4189)

# Summary

Introduce an admin-only Community health score panel within the global Insights dashboard that provides a monthly breakdown of the Community health score and its underlying metrics, along with historical score tracking. Also make the historical tracking available on locale Insights dashboards.

# Motivation

Currently, the Community health score is calculated via a series of moz-l10n scripts and Google Sheets formulas, collected manually on a monthly basis. Other than the tedious nature of needing to do this manually, PMs need better options to analyze CHS data directly from Pontoon.

# Feature explanation

## Community health score aggregation

On the first day of each month, a scheduled job collects telemetry on the state of each locale for the **previous month**. The data collected for **each locale** is compiled into the following metrics:
- `active_managers`: Managers whose combined total of performed reviews and approved translations during the past 12 months exceeds 500.
- `active_translators`: Translators whose combined total of performed reviews and approved translations during the past 12 months exceeds 400.
- `active_contributors`: Contributors whose approved translations during the past 12 months meets or exceeds 200.
- `all_contributors`: Contributors whose combined total of approved translations, rejected translations and pending suggestions during the past 12 months meets or exceeds 200.
- `new_signups`: New signups whose approved translations during the past 12 months meets or exceeds 100.
- `key_projects_enabled`: Number of projects that are classified as key projects via the `is_chs_project` flag.
- `completion`: Locale completion, expressed as a percentage of **approved strings** + **strings with warnings** out of **total strings**.

The data used is then computed into the following scores based on predetermined thresholds. Finally the scores are summated to a **Community health score** for that locale on that month which is used for measuring locale health.

## Community health score panel

The new **Community health score** panel located at `/insights` consists of a widget, a table of locales and a graph.

The widget at the top of the panel contains **locale search** and buttons titled `Edit Locales` and `Show scores`. `Edit Locales` swaps the panel contents for a selector that enables admins to change locale availability on the CHS panel. `Show scores` toggles default and score view of components that make up the CHS.

The table of locales represents the locales the admin wishes to observe based on the most recent month's CHS data. Each table row contains the following information:
- **Locale code** linking to individual locale pages
- Number of **active managers**
- Number of **active translators**
- Number of **active contributors**
- Number of **all contributors**
- Number of **new signups**
- Number of **enabled key projects** (%)
- Overall locale **completion** (%)
- CHS

Beside each statistic, an up/down arrow combined with a number represents the delta over the previous month's statistic. Data that has no change is not represented with a delta. For counts (contributor, translator, manager counts etc.), each value is represented as an integer. For the scores and percentages, each value is represented with 2 decimal places.

The chart is a line chart that displays Community Health Score (CHS) values for the selected locales over the past 12 months. Hovering over any data point displays a tooltip with the exact CHS value for that month for all selected locales. The legend lists individual locales along with `Average (all locales)` and allows each line to be shown or hidden.

## Locale Insights changes

A new graph called `Community health score` is added to the [locale insights page](https://github.com/mozilla/pontoon/blob/main/specs/0108-community-health-dashboard.md), which shows the CHS values for the locale over the past 12 months.
