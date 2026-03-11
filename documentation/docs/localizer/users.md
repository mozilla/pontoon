# User Accounts & Settings

## Roles and permissions

Users in Pontoon are assigned one of four roles, each with different capabilities:

<span class="role-badge role-contributor">Contributor</span>
: The default role for new users. Can submit translation **suggestions** only; suggestions must be reviewed and approved by a Translator or Team Manager before they appear in the product.

<span class="role-badge role-translator">Translator</span>
: Can submit **approved translations** directly and **review** suggestions from other users. Can also manually switch to Suggestion Mode if preferred. Translators need access to contributor contact details for review, so their email addresses are visible to translators by default.

<span class="role-badge role-manager">Team Manager</span>
: Has all Translator capabilities, plus can **manage permissions** for other users within their locale. Responsible for maintaining team quality and unreviewed suggestion queues.

<span class="role-badge role-admin">Administrator</span>
: Can manage all aspects of Pontoon — adding/removing projects, acting as a Team Manager for all locales, and accessing the admin console.

Additionally, **Project Managers** are not a permission level but a point of contact designation for a specific project. Their names appear in project headers, and they are tagged when contributors use REQUEST CONTEXT or REPORT ISSUE.

## Managing permissions (Team Managers)

To manage user permissions, open the **Team page** → **Permissions** tab (visible only to Team Managers and Administrators).

The permissions panel has a **General** section by default. Permissions defined here apply to all projects for the locale, but can be overridden by project-specific custom permissions.

To move a user between permission levels, hover their email address — arrows will appear to move them left or right between columns. Click **SAVE** before leaving the window.

!!! note
    A user must log in to Pontoon at least once before their permissions can be changed.

By default, the TEAM CONTRIBUTORS column shows only users who have already submitted suggestions for the locale. Click **ALL USERS** to display all Pontoon users, then use the search field to narrow down.

### Custom permissions per project

Click **ADD CUSTOM PERMISSIONS PER PROJECT** to set permissions for a specific project. This is useful if a project is maintained by a dedicated person or a restricted group. Custom project permissions override the General section for that project.

!!! warning
    If a user needs to translate **all** projects, they must be listed in every custom permissions section **and** in the General section.

## Account settings

Access account settings via the profile icon in the top-right corner.

### Personal preferences

| Setting | Description |
|---|---|
| **Make suggestions** | Switches a Translator or Team Manager to Suggestion Mode by default. |
| **Default homepage** | Choose between Pontoon's homepage or a specific Team page as your landing page after login. |
| **Preferred source locales** | Display a different source locale when translating (Mozilla projects use `en-US` as the default). |
| **Preferred locales** | Pin specific locales to appear first in the LOCALES tab when reviewing translations. |

### Profile visibility

Control who can see specific profile fields:

| Field | Default visibility | Can be changed to |
|---|---|---|
| Email address | Translators only | All logged-in users (never public, to prevent spam) |
| External accounts | Translators only | Public |
| Approval rate / Self-approval rate | Public | Translators only |

!!! note
    Team and Project Managers always have their email address visible to logged-in users, regardless of visibility settings.

### Email notifications

Control which Pontoon emails you receive, including notification digests and news updates.

!!! note
    Opting out of *News and updates* prevents you from receiving Messaging Center emails unless the message is marked as **Transactional** by the sender.
