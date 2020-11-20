- Feature Name: Concordance Search
- Created: 2020-07-07
- Associated Bug: https://bugzilla.mozilla.org/show_bug.cgi?id=1514698

# Summary

Add ability to search existing translations while translating or reviewing strings.

# Motivation

Having the ability to search for existing translations is a crucial tool for assuring translation consistency. It allows you to see how was the same expression translated in the past or verify that the translation you intend to use is consistent with the rest of the corpus. Pontoon tries to automate that as much as possible with Machinery suggestions by querying Translation Memory as soon as a string is opened for translation.

That being said, Translation Memory is only queried for strings as a whole, even if you "Search in Machinery". If you're interested in the translation of a word "file", but your corpus only uses that word as part of longer strings like "Select a file..." or "Source file uploaded", Machinery won't find any matches.

Alternatively, you can switch to the All Projects view and use the string list search, which searches for substrings within existing translations for each word separately, but that also comes with a few drawbacks. You either lose translation progress in the editor and the state of the string list, or you need to use a separate tab. You also won't be able to search for translations in the projects that aren't active anymore.

# Feature explanation

This feature changes the way "Search in Machinery" searches Translation Memory. Instead of searching for fuzzy matches of source strings stored in TM, it searches source strings and translations stored in TM with the same approach that is used in the string list. Every search keyword is searched separately, unless it's part of a phrase within double quotes - in this case the entire phrase within the quotes is searched as a whole.

Some examples of search queries and corresponding search matches among the two strings mentioned above:
* File -> Select a `file`... & Source `file` uploaded
* Source file -> Select a `file`... & `Source` `file` uploaded
* "Source file" -> `Source file` uploaded

To help with the implementation, see `Entity.for_project_locale()` in `pontoon.base.models`, which is used for string list search. The important difference is that Concordance Search searches only `source` and `target` fields of the `TranslationMemoryEntry` (instead of several different fields of the Entity and Translation models).

Two changes are made to the search box. Placeholder text is changed from "Search in Machinery" to "Search Translation Memory" and the magnifier icon is changed from [fa-search](https://fontawesome.com/icons/search) to [fa-times](https://fontawesome.com/icons/times) when results for Concordance search are displayed. Clicking on it reverts to the default Machinery results.

In output, results are sorted by Levenshtein distance in descending order. Project name is used as the title instead of "Translation Memory", unless `TranslationMemoryEntry.project` field is None. Clicking on each result adds the text to the editor (like when inserting Terms) instead of replacing its content (like when using default Machinery results).

Search behaviour of other sources (e.g. Machine Translation) remains unchanged.
