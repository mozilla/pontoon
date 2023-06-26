- Feature Name: Pretranslation Opt-in UI
- Created: 2023-06-26
- Associated Issue: #2893

# Summary

Locales, if supported by the pretranslation provider, should be able to opt in to the pretranslation feature directly from Pontoon.

# Motivation

After testing pretranslation with a limited number of locales, we believe the feature is ready for larger adoption. In order to support this expansion, locales need to be able to opt in directly from Pontoon, selecting projects for which they want to start using pretranslation.

# Feature explanation

Provide a `REQUEST PRETRANSLATION >` button in the team page, similar to `REQUEST MORE PROJECTS >`.

The conditions for displaying the button are:
* The current user is a translator or manager for the locale (the button is not available for contributors).
* The locale is supported by the pretranslation provider (currently Google AutoML).
* There are available projects where pretranslation is not enabled yet for the locale.

When clicked, the button shows a list of available projects that can be selected via checkbox. When selecting one or more projects, the following text is displayed at the bottom of the list:

> Pretranslation won’t be enabled automatically for the requested projects: an email will be sent to Pontoon admins and team managers to evaluate the request. Note that, if a locale is not using pretranslation yet, this will require additional time to train a custom translation engine.

This text is followed by a `REQUEST PRETRANSLATION` button. When clicked, the button’s text changes to `ARE YOU SURE?`, asking for a confirmation before sending the actual request.

At the end of the process, an email is sent:
* Subject is `Pretranslation request for $LOCALE_NAME ($LOCALE_CODE)`.
* Recipients are the requester, the locale managers, and `pontoon-team@mozilla.com`.
* The message body must include:
    * The list of projects requested, and a link to the requester’s profile page.
    * A warning if the locale doesn’t have any projects enabled for pretranslation yet.

Example of email, including a warning as a new locale:

```
Subject:
Pretranslation request for Portuguese (Portugal) (pt-PT)

Body:
IMPORTANT: Pretranslation is not enabled yet for this locale. Training a custom engine is required before enabling new projects.

Please enable pretranslation for the following projects in Portuguese (Portugal) (pt-PT):
- Firefox Multi-Account Containers Add-on (firefox-multi-account-containers)

Requested by $CONTRIBUTOR_NAME <$CONTRIBUTOR_EMAIL>, $CONTRIBUTOR_ROLE:
$CONTRIBUTOR_PROFILE_URL
```
