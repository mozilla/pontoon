Feature Development Process
===========================

Landing a new feature or significant change in Pontoon follows a structured yet flexible process. The goal is to ensure high-quality, well-considered contributions that align with project priorities and community needs.

.. contents:: Table of Contents
   :depth: 1
   :local:

Propose the Idea (Filing an Issue)
----------------------------------

Anyone can suggest improvements: new features, enhancements to existing ones, or feature removals.

* For trivial changes (typos, minor bugfixes), a pull request (PR) alone may suffice—no dedicated issue required.
* For anything non-trivial, create a GitHub issue in the mozilla/pontoon repository.
  * Clearly describe the problem/opportunity.
  * Explain the motivation, expected impact, and user value.
  * Include relevant context (screenshots, use cases, alternatives considered).

Triage
------

Core maintainers review new issues and perform triage on a weekly basis to assign:
* Type: Bug, Feature, Task.
* Priority label: P1 (must be fixed immediately) to P5 (valid bug, but you might need to fix it).
* Labels such as “needs: specification” or “needs: documentation” if required.
* Labels for rough time estimate: hours, days, weeks, months, quarters.

The issue is added to the Pontoon Roadmap GitHub project:
* Initially placed in “Needs triage”.
* Moved to “Ready” once actionable.
* Kept in “Not ready yet” if more discussion or a spec is needed.
* High-priority items ready for near-term work move to the top of the “Ready” column.
* Larger initiatives (estimated to take months or quarters) are always kept in the "Not ready" column before they are split into smaller issues.

Specification (Recommended for Larger Features)
-----------------------------------------------

For medium-to-large features (those affecting UX flows, data models, multiple areas, or needing community consensus):
* Draft a specification document in Markdown format and submit it as a PR to the specs/ folder.
* Follow the structure seen in existing specs (problem statement, goals, user stories, proposed solution, impacted areas, risks, alternatives, migration plan if applicable).
* Get feedback and approval from core team members.

Once approved, remove any “needs: specification” label and move the issue to “Ready” on the Roadmap.

Implementation (Writing Code)
-----------------------------

* When ready to begin, assign yourself or get assigned to the issue.
* The issue will then move to “In Progress” on the Roadmap.
* Work in a feature branch.
* Deliver:
  * Clean, complete code.
  * Unit and integration tests with good coverage.
  * Any necessary database migrations or data changes.

Code Review
-----------

* Open a pull request targeting the “main” branch.
* Make sure CI tests pass.
* Review will be automatically requested from core Pontoon team members.
* Address feedback on code quality, security, performance, test coverage, and best practices.
* Once approved, the PR is merged.
* The associated issue is closed and moved to “Done” on the Roadmap.

Testing
-------

* The contributor is primarily responsible for thorough testing.
* Verify the feature behaves as intended.
* Check for regressions.
* For larger features, perform extensive testing in the development environment during/after review.
* Core team may run additional testing.

Release
-------

* Features are first deployed to the development environment for final validation.
* Once confirmed stable, they go live on production.
* Deployments are handled by core maintainers and occur as changes are ready (typically immediately after, no strict cadence).

Documentation & Discoverability (as Needed)
-------------------------------------------

* If labeled “needs: documentation” or if the change affects users noticeably:
  * Update or add content in the Pontoon documentation for localizers.
* For major or high-impact features:
  * Core team may add in-app announcements.
  * The contributor might write a blog post on the Mozilla L10n blog.
