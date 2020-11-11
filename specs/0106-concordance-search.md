- Feature Name: Concordance Search
- Created: 2020-07-07
- Associated Bug: https://bugzilla.mozilla.org/show_bug.cgi?id=1514698

# Summary

Add ability to search existing translations while translating or reviewing strings.

# Motivation

Having the ability to search for existing translations is a crucial tool for assuring translation consistency. It allows you to see how was the same expression translated in the past or verify that the translation you intend to use is consistent with the rest of the corpora. Pontoon tries to automate that as much as possible with Machinery suggestions by querying Translation Memory as soon as a string is opened for translation.

That being said, Translation Memory is only queried for strings as a whole, even if you "Search in Machinery". If you're interested in the translation of a word "file", but your corpora only uses that word as part of longer strings like "Select a file..." or "Source file uploaded", Machinery won't find any matches.

Alternativelly, you can switch to the All Projects view and use the string list search, which searches for substrings within existing translations for each word separatelly, but that also comes with a few drawbacks. You either lose translation progress in the editor and the state of the string list, or you need to use a separate tab. You also won't be able to search for translations in the projects that aren't active anymore.

# Feature explanation

This feature changes the way "Search in Machinery" searches Translation Memory. Instead of searching for fuzzy matches of whole strings stored in Translation Memory, `source` and `target` fields of the `TranslationMemoryEntry` model are searched for each keyword and each phrase within quotes separately.

For inspiration, see `Entity.for_project_locale()` in `pontoon.base.models`, which is used in string list search. Note that only `source` and `target` fields are used for searching (unlike in `Entity.for_project_locale()`, which also searches comments).

Placeholder text of the search box is changed from "Search in Machinery" to "Concordance Search". When results for Concordance search are displayed, the magnifier icon in the search box changes from fa-search to fa-times. Clicking on it reverts to the default Machinery results. In output, project name is used as the title instead of "Translation Memory", unless `TranslationMemoryEntry.project` field is None.

Search behaviour of other sources (e.g. Machine Translation) remains unchanged.
