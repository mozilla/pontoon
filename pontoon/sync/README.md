# Translation Sync

At it's core, Pontoon is a user interface for editing translations that are
stored in a version control system. Because Pontoon does not directly edit the
VCS files whenever a user submits a translation, it has to maintain a database
of what it thinks the translated strings are. And, periodically, it has to sync
with version control to pull newly-submitted strings and translations committed
directly, as well as to write its own changes back.

This document describes that sync process in detail.

## Triggering a Sync

Pontoon is assumed to run a sync regularly, at a configurable interval.
When a sync is triggered, Pontoon finds all projects that are not marked as
disabled within the admin interface and schedules a sync task for each one.
Sync tasks are executed in parallel, using [Celery](http://www.celeryproject.org/)
to manage the worker queue.

## Syncing a Project

Syncing an individual project is split into multiple steps:

1. Pull latest changes of all project repository or repositories from version control.

2. Identify the source resources that have changed or been added to the version control repository,
   and synchornize their changes into the database.

3. Identify the target resources that have changed or been added to the version control repository,
   and synchornize their changes into the database.
   If a translation has simultaneously changed in Pontoon as well as version control,
   the version in Pontoon is retained.

4. Identify the translations that have changed in Pontoon,
   and synchornize their changes into version control.
