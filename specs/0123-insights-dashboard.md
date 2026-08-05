- Feature Name: Community health score (CHS) panel
- Created: 2026-08-04
- Associated PR: [#4189](https://github.com/mozilla/pontoon/pull/4189)

# Summary

Introduce an admin-only dashboard within `/insights` where PMs can observe the monthly changes to the Community Health Score through a deconstruction of its algorithm, and implement additional statistics tracking within global and locale Insights pages for PM ingestion.

# Motivation

Currently, the CHS is calculated via a series of moz-l10n scripts and Google Sheets formulas, collected manually on a monthly basis. Other than the tedious nature of needing to do this monthly, PMs need better options to analyze CHS data holistically.

# Feature explanation

## Community health score activity

This feature located at `/insights` consists of a table of locales similar to the `/teams` page, and a multi-line graph.

- Top menu title: `Community health activity`
- Dashboard:
  - Widget: contains locale search and buttons titled `Configuration` and `Show Scores`
    - `Configuration`: links to a separate page that enables admins to change locale availability on the dashboard and CHS activity graph
    - `Show Scores`: toggles default and score view of components that make up the CHS
  - Layout: tabular
  - Each row contains the following information:
    - Locale code linking to individual locale pages
    - \# of managers with > 500 submissions trailing 12 months / 1
    - \# of translators with > 400 submissions trailing 12 months / 2
    - \# of contributors with > 200 submissions trailing 12 months / 2
    - \# of contributors (all) this month / 2
    - \# of new signups with > 100 submissions / 2
    - \# of enabled projects / total # of key projects * 100%
    - Overall completion percentage of locale
    - CHS, written as a float
  - Beside each statistic, an up/down arrow combined with a smaller number, indicating increase or decrease, presents the delta over the previous month's statistic. Data that has no change is not represented with a delta.
  - Value formatting:
    - For counts (contributor, translator, manager counts etc.), each value is an integer without exception.
    - For the scores and percentages, each value is fixed at 2 places (e.g. `20.00`) without exception.
- Graph:
  - Tooltip: describes basic functionality, which is to track CHS per locale
  - Legend: contains locales and `Average (all locales)`, which can be selected/deselected to display corresponding CHS datapoints over time.
  - Display: displays CHS scores for selected locales trailing 12 months. As soon as the CHS calculation automation on Pontoon runs on the first of each month, the previous month's scores will be automatically available for display.

## Insights Configuration

The dashboard page has a button named `Edit Locales`. Upon clicking it, admins are redirected to a locale selector that enables them to add/remove locales from their dashboard view.

## Locale Insights changes

The `/<locale-code>/insights/` page currently includes statistics and useful information regarding locale health and performance. The main change includes a new graph as follows:

- Graph:
  - Name: `Community health score`
  - Tooltip: describes basic functionality, which is to track CHS of current locale
  - Display: displays CHS scores for current locale trailing 12 months. As soon as the CHS calculation automation on Pontoon runs on the first of each month, the previous month's scores will be automatically available for display.
