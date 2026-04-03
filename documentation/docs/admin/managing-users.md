# Managing Users

## Deactivating users

Deactivating a user prevents them from logging in but preserves their contribution history and attribution in translation records.

1. Access Django's admin interface at `/a/`.
2. Click **Users** and search for the user.
3. Uncheck the **Active** checkbox on the user's record.
4. Click **Save**.

Deactivation is reversible — you can reactivate the user by checking **Active** again.

## Removing users

Removing a user **permanently deletes** their account. This is irreversible and should only be done when strictly necessary (e.g., for GDPR/privacy requests).

1. Access Django's admin interface at `/a/`.
2. Click **Users** and search for the user.
3. Select the user and choose **Delete selected users** from the action dropdown.
4. Confirm the deletion.

!!! danger
    Deleting a user is permanent. Their username may be replaced with an anonymized placeholder in historical translation records.

## Adjusting permissions

To change a user's role (Contributor, Translator, Team Manager), use the **Permissions** tab on the relevant Team page. See [User Accounts & Settings](../localizer/users.md#managing-permissions-team-managers) for details.
