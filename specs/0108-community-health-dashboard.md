- Feature Name: Community Health Dashboard
- Created: 2020-10-23
- Associated Bug: https://bugzilla.mozilla.org/show_bug.cgi?id=1672966

# Summary

Create a team-specific health dashboard targeted at Pontoon users with Manager rights.

# Motivation

Team managers as well as project managers should have the ability to understand how localization communities are performing. Team dashboards already provide some of the answers, including the overall status of completion and translation statistics, but the information is only available in form of a current snapshot.

There's no historic data to provide insights into how the community health is developing. Missing is the information on how completion and the volume of unreviewed strings are changing over time. It's also not clear what share of translations went through a proper review process, what share was self-approved and what share of translations was copied from the Machinery.

# Out of scope

At this stage we’re only interested in presenting data we already collect in Pontoon. We're primarily focusing on exposing data to team managers; project managers will be able to obtain data across all teams if needed, e.g. by using scripts and the API.

# Feature explanation

A new "Insights" tab is made available on the Team page, positioned next to the "Contributors" tab. It consists of several sections, presenting data for the period of the last 12 months. Each of the sections in described below. Fore more details about the design, see the [Mockup](#mockup) section.

## Active users

Pie charts showing ratios of active vs. all managers, reviewers and contributors. See the existing scripts ([1](https://github.com/flodolo/scripts/blob/master/pontoon/active_contributors.py), [2](https://github.com/flodolo/scripts/blob/master/pontoon/list_reviewers_with_contribution_stats.py)) for criteria of defining active users and for details on how to retrieve data.

## Average review lag

A line chart showing average unreviewed suggestion lifespans over time. See the [existing script](https://github.com/flodolo/scripts/blob/master/pontoon/unreviewed_suggestions_lifespan.py) for details on how to retrieve data. A tooltip showing exact data at the given time appears when hovering a chart.

## Translation activity

A combination of a line chart showing completion over time and a column chart showing approved translation submissions and source string additions over time in two separate columns. The translation submission column is a stack of two columns - human translations and Machinery translations. A tooltip showing exact data at the given time appears when hovering a chart.

See the [existing script](https://github.com/flodolo/scripts/blob/master/pontoon/self_approval_ratio.py) for calculating self-approval ratio.

## Review activity

A combination of a line chart showing volume of unreviewed strings over time and a column chart showing review actions and suggestion submissions over time in two separate columns. The review actions column is a stack of three columns - peer-approvals, self-approvals and rejections. A tooltip showing exact data at the given time appears when hovering a chart.

# Retrieving data

Data doesn't need to be calculated on the fly. A (daily) cron job gathers all the required data for plotting charts and stores it in the DB. A data migration is used for gathering data for the past 12 months.

We already have scripts for retrieving most of the data (linked in the [Feature explanation](#feature-explanation) section). For the rest, the ActivityLog model is used as much as possible for improved performance over e.g. Translation and Entity models.

# Mockup

![](0108/mockup.png)
