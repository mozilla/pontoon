* Feature Name: Infobar Component
* Created: 2021-02-25
* Associated Bugs: [bug 1694911](https://bugzilla.mozilla.org/show_bug.cgi?id=1694911)

# Summary

Create a reusable component to display infobars to users.

# Motivation

We need a flexible way to notify users without writing ad-hoc code for every situation:
* Infobars should be manageable by admins without intervention from developers.
* Unlike notifications, infobars are more visible and require interaction from users to get dismissed.

Example use case: we introduce a brand new feature, like string comments, and we want to make sure that users are aware of it. The infobar will include a short message and a link to documentation.

# Feature explanation

When a logged in user opens Pontoon, we check against a list of infobars. If the user matches the necessary conditions, we display the infobar.

Information about each infobar is stored in a table with the following fields:
* Identifier: short text identifier, e.g. `new_terms_2020`.
* Start time (datetime): when we should start displaying the infobar to users.
* End time (datetime): when we should stop displaying the infobar to users.
* Creation date (date): stores when the infobar was created.
* Cohort: if defined, we only display the infobar for users part of a specific experiment or cohort (A/B testing).
* Type: `infobar`, `modal`. Infobar is displayed at the top of the window, while modal is displayed in the middle of the window.
* Title: (optional) title for the infobar.
* Text: (mandatory) text for the infobar. Basic HTML should be allowed.
* Button: text for the button. If empty, the button will not be displayed. The only action associated to a button would be opening the associated URL. The button is mandatory for `modal`, optional for `infobar`.
* URL: URL to open when the user clicks the button. Mandatory if the button field is populated.

For each user, we need to store if an infobar has been dismissed, to avoid displaying it again. We store that information in a table with the following fields:
* User ID.
* Infobar ID.
* Action date (datetime).

We also want to keep track of every time we display the infobar to each user. Every display action will be logged in a table with the following fields:
* User ID.
* Infobar ID.
* Action date (datetime).

# Dismissing infobars

For the `infobar` type, the infobar won’t be displayed to the user again if:
* They click the close (x) button.
* They click the button, if present.

For `modal` infobars, it won’t be displayed to the user again only if they click the button, which has to be present. The infobar won’t have a close button (x).

# Multiple infobars

If there are multiple infobars active, we only display the most recent based on creation date.

# Out of scope

* Writing a dashboard to manage infobars is out of scope. For the initial phase, working directly via the Django Admin interface would be sufficient.
* Tracking changes to existing infobars.
