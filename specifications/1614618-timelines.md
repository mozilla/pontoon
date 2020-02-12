- Feature Name: Timelines
- Bug: [bug 1614618](https://bugzilla.mozilla.org/show_bug.cgi?id=1614618)

# Summary

Add Timelines to Projects to educate localizers on future milestones on a
project that's continuously shipping.

# Motivation

Pontoon currently supports Deadlines. They're one-off points in time, and they
pose a few limitations:

* Deadline sounds permanent, threatening, and ugly.
* Project managers can't set more than one.
* In practice, many deadlines are in the past.
* Most projects at Mozilla continue to ship past a deadline.

# Roles

| Role | Impact |
| -- | -- |
| Localizer | Only see upcoming points in time |
| L10n Project Manager (LPM) | Set multiple points in time for a project |

# New Roles

| Role | Impact |
| -- | -- |
| Project Manager (PPM) | PPM can set multiple points in time for a project|

This feature introduces a role of the upstream project manager. In contrast to
the Localization Project Manager (LPM), this is a Project Project Manager, thus
we're introducing the acronym PPM.

# Feature Explanation

Timelines introduce a concept of multiple points in time that have impact to
localizers. The points in time shown to localizers are always relevant to what a
localizer does right now.

For PMs these points in time (PIT) will have labels that help to recognize which
PIT is which. That way, if schedules change, PMs can update the corresponding
PIT easily.

Example: In Android L10n, we might have PITs for releases of Android Components
every two weeks, a PIT for the next cut-off for a Fenix release, and a PIT for
the next cut-off for a Lockwise release.

*TBD*: Should metadata like labels be shown to Localizers?

*TBD*: Should we show the latest PIT if there's no upcoming one? Should we do
that only for some amount of time?

*TBD*: Can there be both a Deadline and a Timeline for a project?

# Data Models

## Point in Time

The basic model for Timelines is a Point in Time.

| Key | Type |
| -- | -- |
| project | ForeignKey(Project) |
| when | datetime |
| label | string |
| author | ForeignKey(User) |
| created_when | datetime |

PITs are deleted when projects are deleted.

*TBD*: Modifications to existing PITs should be traced in a log. Is ActionLog
the right place?

*TBD*: What to do when a User is deleted?

# Phases

This feature can be implemented incrementally.

## Basic Functionality

In this phase, we're not yet introducing new roles, and the management of
Timelines is done by LPM.

## Extended Management

In addition to LPMs, we add the ability for Project Project Managers (PPM) to
maintain the Timeline data.

*TBD*: Should PPMs manage date changes, or also PIT creation and metadata like
labels?

*TBD*: Are there constraints of how soon a PIT can be?
