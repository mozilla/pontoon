# Community Health Score

The Community Health Score (CHS) is a heuristic score, represetned as a single number between 0 and 100, intended to provide insight into a localization team's health. The number represents a combination of the current state of community members actively contributing to a locale and the localization status of key projects.

## What the score is for

Community localization teams rely on the volunteer participation of a number of contributors supporting one another in a variety of roles. Robust teams with active team managers, translators, and contributors are better able to create and sustain a thriving community that can ensure projects are translated at a high completion level over the long-term. 

While communities can and do ensure projects are translated to a high-level of completion with sometimes just one or two people, the Community Health Score exists to make those less-sustainable situations more visible and to track changes in health over time. It is designed to answer questions like:

* Does the team have people in every role it needs, or does it depend on a single person?
* Is a team attracting new active contributors?
* Is a team keeping up with the projects they have enabled?
* How is the team’s situation changing compared to previous months?

The score is designed for project managers to spot opportunities for improving a community's health, it is not a grade or judgement on a team's performance. A low score isn’t a judgement on the quality of a team’s efforts, and a high score doesn’t mean there’s nothing to improve.

## How the score is calculated

The score is calculated once a month. On the first day of each month, Pontoon takes a snapshot of every team: it measures the seven criteria described below, converts each one into points, and adds them up. The result is that month’s Community Health Score.

| Criterion | Maximum points | What it measures |
| --- | --- | --- |
| [Active managers](#active-managers) | 20 | Team managers actively submitting or reviewing contributions above a certain threshold |
| [Active translators](#active-translators) | 15 | Translators actively submitting or reviewing contributions above a certain threshold |
| [Active contributors](#active-contributors) | 6 | Contributors actively making contributions that have received reviews above a certain threshold |
| [All contributors](#all-contributors) | 4 | All contributors who have submitted suggestions above a certain threshold |
| [New signups](#new-signups) | 5 | Newly joined contributors who have submitted suggegot above a certain threshold|
| [Enabled key projects](#enabled-key-projects) | 4 | How many key projects the team has enabled |
| [Project completion](#project-completion) | 46 | Percentage of strings translated in key projects |
| **Total** | **100** | |


### Active managers

**20 points.** [Team managers](users.md#user-roles) who did a substantial amount of work in the team during the measured window.

A manager qualifies when their **review actions plus their own approved translations exceed 500** for the team. Review actions are approvals and rejections they performed on other people’s translations; self-approvals that happen automatically when a manager submits a translation are not counted twice.

Unlike the other people criteria, one qualifying manager is enough for the full 20 points. A team with no active manager loses a fifth of the total score — this is the strongest single signal in the score, because a team without an active manager has no one to organize the community, manage permissions or respond to requests.

### Active translators

**15 points.** [Translators](users.md#user-roles) — contributors with review rights, who are not also managers — who did a substantial amount of work in the team during the measured window.

A translator qualifies when their **review actions plus their own approved translations exceed 400** for the team. As with managers, automatic self-approvals are not counted twice. Two or more qualifying translators earn the full 15 points, one earns 7.5, none earns 0.

Having a number of active translators are vital for a community's health, ensuring that other contributor's submissions are reviewed in a timely fashion ensures new contributors are more inclined to remain part of the community.

### Active contributors

**6 points.** Contributors without review rights whose work is being accepted into the product.

A contributor qualifies when they have **at least 200 approved translations** for the team within the measured window. Two or more qualifying contributors earn the full 6 points, one earns 3, none earns 0.

Having a number of active contributors who are receiving feedback from other community members is a good sign of a stable community fostering long-term development of fellow volunteers.

### All contributors

**4 points.** Contributors without review rights who are submitting a substantial volume of work, regardless of whether it has been reviewed yet.

A contributor qualifies when they have submitted **at least 200 translations** for the team within the measured window, in any state — approved, pending review or rejected. Two or more qualifying contributors earn the full 4 points, one earns 2, none earns 0. Note, this is inclusive of active contributors.

Having a strong contributors base is important for the sustainability of the community. This criteria also provides insight into whether contributors are receiving reviews of their submissions, which is important for encouraging continued participation.

### New signups

**5 points.** People who both joined Pontoon and got meaningfully started in the team during the measured window.

A new signup qualifies when their account was **created within the window** and they have **at least 100 approved translations** for the team. The approval requirement is deliberate: it measures onboarding that worked, not registrations. Two or more qualifying new signups earn the full 5 points, one earns 2.5, none earns 0. This is the criterion that reflects whether a team is renewing itself.

New signups is an indicator of whether a community is attracting new interested community members, and a good signal for reaching out and connecting with the new contributor to onboard into the community.

### Enabled key projects

**4 points.** How many of the [key projects](#key-projects) the team is enabled for, as a share of all key projects.

Points are awarded in proportion: a team enabled for all key projects earns all 4 points, a team enabled for half of them earns 2. Projects that have been disabled are not counted on either side.

A team can raise this number by [requesting a project](teams-projects.md#requesting-a-project) from its team page. Note that taking on more projects also adds untranslated strings, which will lower [project completion](#project-completion) until the new work is done, so should only be considered if the community can handle the increased and ongoing workload from the new project.

### Project completion

**46 points.** The share of strings the team has completed in [key projects](#key-projects), where a string counts as completed if it is approved — including approved translations that carry a warning.

Points are awarded in proportion to that percentage: a team at 100% completion earns all 46 points, a team at 50% earns 23, a team at 20% earns 9.2. This is by far the largest single criterion, and the one most directly under a team’s control.

## Improving a team’s score

In rough order of impact:

1. **Translate and review key project strings.** Completion is worth 46 points, more than any other criterion, and it responds immediately.
2. **Make sure the team has an active manager**, and ideally more than one person with review rights. Together these are worth 35 points, and they unlock the contributor criteria as well: nothing gets approved without reviewers.
3. **Review pending suggestions.** A backlog costs points twice — in completion, and in [active contributors](#active-contributors) — and it discourages the people waiting for feedback.
4. **Welcome and retain new contributors.** New signups only count once they reach 100 approved translations, so responding quickly to a newcomer’s first suggestions is what turns a registration into points.
5. **Request the key projects your team can realistically handle.** Enabling a project you don’t have capacity for will cost more in completion than it gains here.

Because scores are recalculated monthly, changes show up in the next snapshot rather than immediately.

## Notes on the numbers

The point values and thresholds documented above are Pontoon’s defaults, and are the ones in use on [pontoon.mozilla.org](https://pontoon.mozilla.org). Every instance of Pontoon can configure them, along with which projects count as key projects, so a self-hosted instance may weigh the criteria differently. Administrators can find the configuration details in the [Insights](../admin/insights.md) documentation.
