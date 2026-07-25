# Insights

Pontoon provides a global **Insights** dashboard for analyzing the health of localization communities and the quality of pretranslations across all locales and projects.

The dashboard is restricted to staff and is available at `/insights` when logged in as an administrator (e.g. [https://pontoon.mozilla.org/insights/](https://pontoon.mozilla.org/insights/) for the instance hosted by Mozilla).

## Community health activity

This section presents a table of the monthly `Community health score` and its underlying metrics for each selected locale. For every team it shows the number of users in different roles — managers, translators, contributors — above a certain threshold of submitted translations, all contributors independently of the number of approved translations, and new signups, along with the number of enabled projects, project completion, and the resulting `Community health score`.

Each cell also displays the month-over-month change, making it possible to compare the current values against the previous month. Use the `Filter teams` search box to narrow the table down to specific locales.

### Edit locales

The `Edit Locales` button toggles a view where the user selects which locales are displayed in the dashboard and its charts. Move one or more locales into the target list to save preferred locales for display. If no locales are selected, the dashboard prompts the user to choose at least one before any data is shown. Press `Back` to toggle back to the dashboard view.

### Show scores

By default the table shows the raw value of each metric. Click the `Show scores` button to switch to the score view, which instead displays the individual component scores that add up to the `Community health score`. Click the button again (now labeled `Show default`) to return to the raw values.

## Community health score chart

This chart plots the monthly `Community health scores` of each selected locale for the most recent 12 months, along with the average of all selected locales. Hover over a data point in the graph to see each selected locale's score for that month along with the average.

## Pretranslation quality

Two charts track the quality of [pretranslations](../localizer/glossary.md#pretranslation) over time, measured as the approval rate of pretranslated strings (the share of pretranslations that reviewers approve rather than reject).

### Team pretranslation quality

Plots the approval rate of pretranslations for each team, making it possible to compare pretranslation quality across locales and spot teams whose custom machine translation models may need attention.

### Project pretranslation quality

Plots the approval rate of pretranslations for each project, highlighting which projects produce the most and least reliable pretranslations.
