* Feature Name: User Notifications Component
* Created: 2021-02-25
* Associated Bugs: [bug 1694911](https://bugzilla.mozilla.org/show_bug.cgi?id=1694911)

# Summary

Create a reusable component to display notifications to users as part of experiments and A/B testing.

# Motivation

We need a flexible way to notify users without writing ad-hoc code for every situation. Notifications should be manageable by admins without intervention from developers.

Potential use cases:
* We introduce a brand new feature, like string comments, and we want to make sure that users are aware of it. The infobar will include a short message and a link to documentation.
* We want to promote the Pontoon add-on. The notification will include a button opening the AMO page to install the add-on.
* We make changes to Pontoon terms and conditions, and want to require users to acknowledge them. The infobar will include a link to the updated terms, and a button to explicitly accept them.

# Feature explanation

When a logged in user opens Pontoon, we check against a list of notifications. If the user matches the necessary conditions, we display the notification.

Information about each notification is stored in a table with the following fields:
* Notification ID (automatically generated).
* Identifier: short text identifier, e.g. `new_terms_2020`.
* Active (boolean): indicates if the notification is currently active or not.
* Creation date (date): stores when the notification was created.
* Cohort: if defined, we only display the notification for users part of a specific experiment or cohort (A/B testing).
* Type: `infobar`, `modal`. Infobar is displayed at the top of the window, while modal is displayed in the middle of the window.
* Title: (optional) title for the notification.
* Text: (mandatory) text for the notification. Basic HTML should be allowed.
* Button: text for the button. If empty, the button will not be displayed. The only action associated to a button would be opening the associated URL.
* URL: URL to open when the user clicks the button.

We also need to store information on the last time we displayed the infobar to each user, to determine if it should be displayed again in the future:
* User ID.
* Notification ID.
* First displayed (timestamp).
* Last displayed (timestamp).
* Number of times it’s been displayed.
* Dismissed (boolean).

If there are multiple notifications active, we look at them in order of creation date, from the most recent to the oldest, to make sure we only display one.

We create a row in the table for the user the first time the notification is displayed, and keep updating the table until it’s dismissed.

For `infobar`, the notification won’t be displayed to the user again (i.e. the `dismissed` field is set to True) if:
* They click the close (x) button.
* They click any of the links included.
* They click the button, if present.

For `modal` notifications, it won’t be displayed to the user again only if they click the button, which has to be present. The notification won’t have a close button (x).

# Out of scope

Writing a dashboard to manage these notifications is out of scope. For the initial phase, working directly via the Django Admin interface would be sufficient.
