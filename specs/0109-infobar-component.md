* Feature Name: Infobar Component
* Created: 2021-02-25
* Associated Bugs: [bug 1694911](https://bugzilla.mozilla.org/show_bug.cgi?id=1694911)

# Summary

Create a component to display infobars to users.

# Motivation

We need a flexible way to notify users without writing ad-hoc code for every situation:
* Infobars should be manageable by admins without intervention from developers.
* Unlike notifications, infobars are more visible and require interaction from users to get dismissed.

Example use cases:
* We introduce a brand new feature, like string comments, and we want to make sure that users are aware of it. The infobar will include a short message and a link to documentation.
* We want to warn users of an upcoming maintenance window for Pontoon.

# Feature explanation

When a logged in user opens Pontoon, we check against a list of infobars. If there is an active infobar, the user belongs to the assigned cohort (where it’s defined) and they haven’t dismissed it yet, we display it.

Information about each infobar is stored in a table with the following fields:
* Identifier: short text identifier, e.g. `new_terms_2020`.
* Start time (datetime): when we should start displaying the infobar to users.
* End time (datetime): when we should stop displaying the infobar to users.
* Creation date (date): stores when the infobar was created.
* Cohort (optional): if defined, we only display the infobar for users part of a specific experiment or cohort (A/B testing).
* Selector (optional): a CSS selector.
    * If empty, the infobar will be displayed at the top of the page.
    * If defined, the infobar will be displayed as a pop-up above the element identified by the selector.
* Pages pattern (optional): regular expression to indicate on which pages the infobar should be displayed.
    * If empty, the infobar will be displayed on all pages.
    * If defined, the infobar will be displayed only on pages whose URL matches the regular expression.
* Title (optional): title for the infobar.
* Text (mandatory): text for the infobar.
    * Basic HTML should be allowed: `<p>`, `<strong>`, `<em>`, `<a>`. For all anchors `target=_blank` will be enforced.
* Button (optional): text for an optional button.
    * The button will not be displayed if this field is empty.
    * The only action associated to a button would be opening the URL specified in the URL field in a new tab.
* URL: URL to open when the user clicks the button.
    * This field is mandatory if the button field is populated.

For each user, we need to store if an infobar has been dismissed, to avoid displaying it again. We store that information in a table with the following fields:
* User ID.
* Infobar ID.
* Action date (datetime).

We also want to keep track of every time we display infobars to each user. Every display action will be logged in a table with the following fields:
* User ID.
* Infobar ID.
* Action date (datetime).

# Dismissing infobars

The infobar won’t be displayed again to the user if:
* They click the close (x) button.
* They click the button, if present.

When one of these actions are performed, the information is stored in the dismissals table.

# Managing multiple infobars

If there are multiple infobars active, we only display the most recent based on creation date.

# Out of scope

The following features are out of scope:
* Writing a dashboard to manage infobars. For the initial phase, working directly via the Django Admin interface would be sufficient.
* Tracking changes to existing infobars.
* Customizing the appearance of the infobars.
