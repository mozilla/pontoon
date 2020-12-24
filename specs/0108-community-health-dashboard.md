- Feature Name: Community Health Dashboard
- Created: 2020-10-23
- Associated Bug: https://bugzilla.mozilla.org/show_bug.cgi?id=1672966

# Summary

Create a team-specific health dashboard targeted at Pontoon users with Manager rights.

# Motivation

Team managers as well as project managers should have the ability to understand engagement of the localization communities. Team dashboards already provide some of the answers, including the overall status of completion and translation statistics, but the information is only available in the form of a current snapshot.

There's no historic data to provide insights into how the community health is developing. Missing is the information on how completion and volume of unreviewed strings are changing over time. It's not clear what share of translations was copied from the Machinery. We also don't know the ratio of translations approved without a peer review.

# Out of scope

At this stage we’re only interested in presenting data we already collect in Pontoon. We're primarily focusing on exposing data to team managers; project managers will be able to obtain data across all teams if needed, e.g. by using scripts and the API.

# Feature explanation

A new "Insights" tab is made available on the Team page, positioned next to the "Contributors" tab. It consists of several sections, presenting data for the period of the last 12 months. Each section is described below. Detailed description of each chart appears when hovering over the info icon. Fore more details about the design, see the [Mockup](#mockup) section.

## Active users

Pie charts showing ratios of active vs. all managers, reviewers and contributors. The observed period of active users can be changed between 12 months (default), 6 months, 3 months, and 1 month.

All managers and all reviewers are taken from the team permissions form. All contributors include all users that have ever submitted a translation for the given team, with system users like Pontoon Sync excluded.

Active users within a selected time frame are defined like this:
* Active managers have logged into Pontoon.
* Active reviewers have performed a review activity (approve, unapprove, reject, or unreject a translation).
* Active contributors have submitted a translation.

Note that only users included in the all users counts can be active users. If a project contact person rejects a suggestion or submits a translation, it doesn't count as an active reviewer or contributor of the team.

## Unreviewed suggestion lifespan

A line chart showing the average age of the unreviewed suggestions in a particular month for a period of last 12 months.

Data is available for each day, but aggregated by month in the chart.

A tooltip showing the exact data at a given month appears when hovering over a chart.

## Translation activity

A combination of two charts:
1. A line chart showing overall completion of team projects over time.
1. A column chart showing translation submissions over time in a stack of two columns - human translations and machinery translations (submitted as unchanged copies of suggestions from Machinery). Translation submissions also include imported translation by sync. New source string additions are plotted in a separate column, which is hidden by default.

Data is available for each day, but aggregated by month in the chart.

A tooltip showing the exact data and ratios at a given month appears when hovering over a chart.

## Review activity

A combination of two charts:
1. A line chart showing the number of unreviewed suggestions of the team over time.
1. A column chart showing review actions over time in a stack of three columns - peer-approvals, self-approvals (translation approvals by their authors, both at the time of submission or later) and rejections. Approvals and rejections performed by sync are excluded. New suggestion submissions are plotted in a separate column, which is hidden by default.

Data is available for each day, but aggregated by month in the chart.

A tooltip showing the exact data and ratios at a given month appears when hovering over a chart.

# Retrieving data

Data doesn't need to be calculated on the fly. A (daily) cron job gathers all the required data for plotting charts and stores it in the DB. A data migration is used for gathering data for the past 12 months.

We already have scripts for retrieving most of the data (linked in the [Feature explanation](#feature-explanation) section). For the rest, the ActivityLog model is used as much as possible for improved performance over e.g. Translation and Entity models.

# Mockup

![](0108/mockup.png)
