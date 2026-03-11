# Renaming a Localization File

Renaming a resource file in the VCS repository requires corresponding updates in Pontoon's database to avoid losing translation history.

## Steps

1. Rename the file in your VCS repository and push the change.
2. Access Pontoon's admin console → the affected project.
3. In the **Resources** section, find the old filename and update it to match the new filename.
4. Save the project and trigger a manual **SYNC**.

!!! warning
    If you sync before updating the resource name in Pontoon, the old resource will be marked as deleted and a new one created, losing all translation history.
