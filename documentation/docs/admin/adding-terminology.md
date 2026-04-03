# Adding New Terminology

To add new terms to Pontoon, access Django’s admin interface at `https://pontoon.mozilla.org/a/` (note that this is not the usual admin interface), then follow the steps below.

Find and click `Terms` on the navigation pane on the left. Check on the following page to make sure a term does not already exist by searching in the search field near the top.

To add a new term, click `ADD TERM +`. The next page will have the following fields:

* Text (required): Term you wish to register.
* Part of speech (required): Select the part of speech that applies to your term. In some cases the same string can be registered twice with different parts of speech, e.g. bookmark as a noun (“open your bookmarks”) or as a verb (“bookmark this website”).
* Definition: Meaning of the term, or explanation of what the term is.
* Usage: Example usage of the term.
* Notes: Any other notes or context that could be relevant.
* Case sensitive: Select if the term should only match when case matches.
* Do not translate: Select if the term should not be translated (example brand names like Firefox).
* Forbidden: Select if this term should not be used.

Once the necessary information has been filled out, click one of the three save options `Save and add another`, `Save and continue editing`, or `SAVE` to register the term to Pontoon.

This term will automatically populate in the terminology projects for all locales for translation, and will also appear in the `TERMS` pane of the translation UI when it appears in a string.

Note that only the following fields are displayed in Pontoon as a localization comment for the term: part of speech, definition, usage.
