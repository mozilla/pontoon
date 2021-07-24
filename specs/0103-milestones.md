- Feature Name: Milestones
- Bug: [bug 1614618](https://bugzilla.mozilla.org/show_bug.cgi?id=1614618)

# Summary

Add Milestones to Projects to educate localizers on future milestones on a
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
| Localizer | Only see upcoming milestones |
| Project Manager (PM) | Set multiple milestones for a project |

# Feature Explanation

Milestones introduce a concept of multiple points in time that have impact to
localizers. The milestones shown to localizers are always relevant to what a
localizer does right now.

For PMs these milestones will have labels that help to recognize which
milestone is which. That way, if schedules change, PMs can update the corresponding milestone easily.

Example: In Android L10n, we might have milestones for releases of Android Components
every two weeks, a milestone for the next cut-off for a Fenix release, and a milestone for
the next cut-off for a Lockwise release.

*TBD*: Should metadata like labels be shown to Localizers?

*TBD*: Should we show the latest milestone if there's no upcoming one? Should we do
that only for some amount of time?

*TBD*: Can there be both a Deadline and Milestones for a project?

# Data Models

## Point in Time

The basic model for Milestones is a an individual milestone.

| Key | Type |
| -- | -- |
| project | ForeignKey(Project, CASCADE) |
| when | datetime |
| label | string |
| author | ForeignKey(User, SET_NULL) |
| created_at | datetime |

Milestones are deleted when projects are deleted.

The change history of Milestones is store in the ActionLog.
