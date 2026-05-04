# Renaming a Localization File

In some cases, project owners will want to rename a file for clarity, or for technical reasons. If it’s only done in the VCS repository, the file will be imported again and you will lose attribution, pending suggestions and history. Since this is a special case, we can work around this and rename the file in Pontoon while keeping existing data (translations, suggestions, attribution, history). The process is not complicated, but it has to be highly coordinated.

## Get a Pull Request ready

Either you or the project owners will get a Pull Request ready that renames the file for all locales. Using a script is recommended as you will need to generate the patch not too long before the next steps to avoid conflicts.

## Rename the resource in Pontoon admin panel

Wait for the current Pontoon sync cycle to end, and make sure you are already logged into Pontoon admin, then merge the Pull Request.

As soon as the Pull Request is merged, go to the [resource section](https://pontoon.mozilla.org/a/base/resource/) of the admin panel, then type the name of your project (e.g. `thimble`) and hit `Enter`. All the resources for your project should appear. Click on the one you want to rename, and in the `path` field, for instance rename `messages.properties` into `server.properties` then click `SAVE`.

It is crucial to do this step **before** the next sync cycle, otherwise the process won’t be effective.

After the next sync, open the file for one of the locales, you should be able to see all the existing data.
