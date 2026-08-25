# Insights

Pontoon provides 2 major systems for admins to monitor locale & project health. The tools
available are the `Insights` dashboard and the `Monthly locale health report`, which both provide
information on locale growth & decline in easily ingestible formats.

## Insights dashboard

Pontoon provides a global **Insights** dashboard for analyzing the health of localization communities and the quality of pretranslations across all locales and projects.

The dashboard is restricted to staff and is available at `/insights` when logged in as an administrator (e.g. [https://pontoon.mozilla.org/insights/](https://pontoon.mozilla.org/insights/) for the instance hosted by Mozilla).

### Community health score

This section presents a table of the monthly `Community health score` and its underlying metrics for each selected locale. For every team it shows the number of users in different roles — managers, translators, contributors — above a certain threshold of submitted translations, all contributors independently of the number of approved translations, and new signups, along with the number of enabled projects, project completion, and the resulting `Community health score`.

Each cell also displays the month-over-month change, making it possible to compare the current values against the previous month. Use the `Filter teams` search box to narrow the table down to specific locales.

#### Edit locales

The `Edit Locales` button toggles a view where the user selects which locales are displayed in the dashboard and its charts. Move one or more locales into the target list to save preferred locales for display. If no locales are selected, the dashboard prompts the user to choose at least one before any data is shown. Press `Back` to toggle back to the dashboard view.

#### Show scores

By default the table shows the raw value of each metric. Click the `Show scores` button to switch to the score view, which instead displays the individual component scores that add up to the `Community health score`. Click the button again (now labeled `Show default`) to return to the raw values.

#### Key projects

Two of the metrics above — the number of enabled projects and project completion — are calculated only across projects marked as key projects, rather than across all projects a team works on. The enabled projects metric is the share of all key projects enabled for the team. The project completion metric is the share of translated strings across the key projects for which the team is enabled. Disabled projects do not count toward either metric, while project completion also excludes system projects and projects that are not visible.

Administrators can mark a project as a key project in the Django admin (`/a/base/project/`) using the `Is chs project` flag. A team counts as enabled for a key project as soon as it is added to that project, just as it would for any other project (see [Adding a new project](adding-new-project.md)).

If no projects are marked as key projects, both metrics are zero for every team. Consequently, the Community health score excludes the points associated with these metrics, and no team qualifies for the [monthly locale health report](#monthly-locale-health-report).

#### Community health score chart

This chart plots the monthly `Community health scores` of each selected locale for the most recent 12 months, along with the average of all selected locales. Hover over a data point in the graph to see each selected locale's score for that month along with the average.

### Pretranslation quality

Two charts track the quality of [pretranslations](../localizer/glossary.md#pretranslation) over time, measured as the approval rate of pretranslated strings (the share of pretranslations that reviewers approve rather than reject).

#### Team pretranslation quality

Plots the approval rate of pretranslations for each team, making it possible to compare pretranslation quality across locales and spot teams whose custom machine translation models may need attention.

#### Project pretranslation quality

Plots the approval rate of pretranslations for each project, highlighting which projects produce the most and least reliable pretranslations.

## Monthly locale health report

Once a month, after new locale health snapshots are collected, Pontoon compares each team’s two most recent Community Health Scores and reports the teams with the largest changes. The report lists each affected team’s score from the previous month, its current score, and the percentage change relative to the previous score. Teams are ordered by the absolute size of the change, largest first, regardless of whether their scores increased or decreased.

A team is included when it is enabled for at least one [key project](#key-projects), has a snapshot in both months, and its score changed by at least 2%. The threshold can be changed through the `MONTHLY_HEALTH_REPORT_CHS_THRESHOLD` environment variable.

Staff users receive the report as a notification in Pontoon. To also receive it by email, enable `Monthly locale health report` in the `Email` section of your [settings](../localizer/users.md).
