# Translation Workspace
Pontoon’s translation workspace consists of the main toolbar and 3 columns:

* The left column contains the string list for the current resource with a search field at the top.
* The middle column contains the main editing space.
* The right column contains terminology, source string comments, suggestions from translation memory, machine translation, and translations from other locales.

![Translation Workspace](../assets/localizer/translation-workspace/translation_workspace.png "Screenshot of the translation workspace in Pontoon")

## Main toolbar

The main toolbar at the top of the page allows users to navigate to the dashboards or to change the current resource.

![Navigating in the main toolbar](../assets/localizer/translation-workspace/main_nav.png "Screenshot of the main toolbar, with the resource dropdown expanded")

Clicking the locale name will open the [Team page](teams-projects.md#team-page) for that locale, while clicking the project name will open the [Localization page](teams-projects.md#localization-page) for that project.

Clicking on the current resource (or `All Resources`) will display a list of all resources available for that project. It’s possible to search for a resource, and click one to load only the entities included in it. Clicking `All Resources` at the bottom of the list will go back to display all resources, while `All Projects` will show entities for all projects under the selected locale.

A progress chart showing the translation status of the current resource is located to the right of the resource name. A more detailed breakdown is displayed when clicking the chart.

![Expanded status overview](../assets/localizer/translation-workspace/status_overview.png "Screenshot of the status graph expanded")

The notifications icon, represented by a bell, is located on the right side of the main toolbar. By clicking the bell icon, users can view a list of the latest [notifications](notifications.md) they received.

The profile menu is located at the far right of the main toolbar. Clicking the profile image will reveal a dropdown menu where users can perform several actions, like navigate to their [profile page](profile.md), [download and upload translations](translate.md#downloading-and-uploading-translations), change their theme, etc.

![Profile menu](../assets/localizer/translation-workspace/profile_menu.png "Screenshot of the profile menu")

Note that some profile menu items are only available to users with specific [permissions](users.md#user-roles).

A selector to change the current theme is available in the profile menu and in the [settings page](users.md#appearance). There are three theme options available:

* Light.
* Dark.
* Match system (aligns with the theme used by the operating system).

To change the theme, select the button corresponding to your preferred theme. The change will take effect immediately.

## String list and search

The left column displays the list of strings in the current project resource. Each string is represented by:

* A colored square that identifies the string [status](#translation-status) (i.e. *Missing*, *Translated*, etc.).
* The source string.
* The approved translation or the most recent suggestion if available.

![Sidebar](../assets/localizer/translation-workspace/sidebar.png "Screenshot of the sidebar, with a list of strings showing the different string statuses")

Color legend:

* **<span style="color: #4d5967;">gray</span>**: translation is missing.
* **<span style="color: #7bc876;">green</span>**: string is translated.
* **<span style="color: #c0ff00;">light-green</span>**: string is pretranslated.
* **<span style="color: #ffa10f;">orange</span>**: translation has warnings.
* **<span style="color: #f36;">red</span>**: translation has errors.

When a string is selected in the sidebar, a small icon with four arrows is displayed near the checkbox: this can be used to show strings that surround the selected string in the [resource](glossary.md#resource), bypassing the current filter. This is often helpful to provide more context for the localization, especially when translating missing strings.

![Button to show sibling strings in sidebar](../assets/localizer/translation-workspace/sidebar_expand.png "Screenshot of the button to show sibling strings in sidebar")

### Search

It’s possible to search within the currently selected project using the search field. Searches include strings and string IDs.

![Search field](../assets/localizer/translation-workspace/search_field.png)

Note that searches take active [filters](#filters) into account, for example a search would be performed only on missing strings if that filter was previously selected.

Like in search engines, by default Pontoon will display matches that contain any of the search terms. For example, searching for `new tab` will match both `Open links in tabs instead of new windows` and `New Tab`.

To search for an exact match, wrap the search terms in double quotes, e.g. `"new tab"`. On the other hand, to search for strings that contain double quotes, escape them with a backslash, e.g. `\"`.

#### Search options

In addition to the search filters listed below, Pontoon provides additional **search options**, allowing users to refine search results. Search options can be accessed by clicking the magnifying glass icon on the right side of the search box.

![Options](../assets/localizer/translation-workspace/options.png)

Search options include:

* **Match case**: exactly match the capitalization of the search term.
* **Match whole word**: provides the same result as surrounding a word with double quotes, exactly matching the search term (case insensitive), and avoiding partial matches.
* **Include string identifiers**: expand the search to include string identifiers (keys).
* **Include rejected translations**: expand the search to include translations that have been rejected.
* **Exclude source strings**: avoid searching for matches in source strings.

When starting a search from the translation workspace, search options follow the user's [default search settings](users.md#default-search-options). If you clicked on a link performing a search, the menu will reflect the parameters used for that specific search — those might be different from your defaults.

Clicking the `APPLY SEARCH OPTIONS` at the bottom of the panel will perform a new search with the selected options. To reset the current options back to the profile defaults, click `Restore default options`. To update the defaults, click `Change default search settings`, which opens the relevant section of the [settings page](users.md#default-search-options).

### Filters

#### Translation status

Strings in Pontoon can be filtered by their status. A string can be in one of the following statuses:

* **Translated**: string has an approved translation. The translation is saved to the localized file when using a [version control system](glossary.md#version-control-system) (VCS).
* **Pretranslated**: string has been pretranslated but has not been reviewed. Unreviewed pretranslation are saved to the localized file when using a VCS.
* **Warnings**: string contains issues classified as [warnings](translate.md#warnings).
* **Errors**: string contains [critical issues](translate.md#errors).
* **Missing**: string doesn’t have any approved translations.
* **Unreviewed**: string has suggested translations that have not been reviewed yet by someone with the appropriate [permissions](glossary.md#permission). Note that, for both translated and missing strings, the suggested translation only exists within the Pontoon database and is not saved to the localized file when using a VCS.

#### Extra filters

In addition to statuses, additional filters can be used to further refine the list of strings. Extra filters include:

* **Unchanged**: string is identical to the reference language (normally `en-US`).
* **Empty**: string has a translation, but translation contains no content.
* **Fuzzy**: string is marked as [fuzzy](glossary.md#fuzzy) in the localized file.
* **Rejected**: string has rejected translations.
* **Missing without Unreviewed**: string has `Missing` translation status and does not have `Unreviewed` translations.

Filters can be accessed by clicking the icon on the left of the search field.

![Filters](../assets/localizer/translation-workspace/filters.png)

At this point it’s possible to:

* Click directly on the name of one of the filters. This will select and activate only this filter, and the search field placeholder will change accordingly. For example, clicking on `Missing` will show only missing strings, and the placeholder will read `Search in Missing`.
* Click on one or more filter icons or user avatars (multiple filters can be applied at once). Hovering over the icons transforms the icon into check marks. Clicking an icon will select that filter and a new button `APPLY X FILTERS` will appear at the bottom of the panel, where `X` is the number of active filters.
* Click `EDIT RANGE` on `TRANSLATION TIME` to select a time range. Pick one of the defaults (30 days, 7 days, 24 hours, 60 minutes), or use the date picker (or slider) to adapt the range. Click on `SAVE RANGE` to store the range as a filter. A new button `APPLY X FILTERS` will appear at the bottom of the panel, where `X` is the number of active filters.

![Multiple filters](../assets/localizer/translation-workspace/filters_multiple.png)

In this case 3 filters are selected.

#### Tags

For specific projects it’s also possible to filter strings based on *tags*. Tags are used to logically group resources based on their priority, allowing localizers to focus their work on important strings first, and project managers to better assess the overall localization status of the project.

![Tags in filters](../assets/localizer/translation-workspace/filters_tags.png)

In this case, there are 10 tags defined for the project (highlighted in red). Near each tag there is a representation of the priority: like for projects, it goes from 5 stars (highest priority) to 1 star (lowest priority).

Note: translation time, translation authors, and tags are not available when `All Projects` is selected as a [resource](glossary.md#resource).

## Main editing space

The main editing space in the middle column is where translation takes place.

![Editing space](../assets/localizer/translation-workspace/editing_space_standard.png "Screenshot of the standard editor in the editing space")

### String navigation

The top of this space contains a string navigation interface. It’s possible to navigate sequentially through the strings by clicking the `PREVIOUS` or `NEXT` buttons located at the top of the editing space, or by using keyboard shortcuts (`ALT` + arrow down or up). A link to the current string can be copied to the clipboard using the `COPY LINK` button.

### Source string

Below the navigation interface, the user can view the source string, any comments present in the resource regarding the string, and the resource path where the string is located.
In the same area, the `REQUEST CONTEXT or REPORT ISSUE` button can be used to request more information about the current string: it will focus the [COMMENTS section](##source-string-comments), and mention the project manager for the project.

#### Context

Sometimes you may want to investigate more context about a particular string through an external resource such as a [Version Control System](glossary.md#version-control-system). The `CONTEXT` information provided underneath the source string shows the identifier, file, and project for the string — allowing you to find the string within the codebase of the project. For example, for some Mozilla projects these can be used to [track strings to bugs](https://mozilla-l10n.github.io/localizer-documentation/tools/mercurial/tracking_back_string_to_bug.html).

![Context](../assets/localizer/translation-workspace/context.png)

### Editor

The editor is located in the middle section of the column, and it’s where users can input or edit their translations.

In the lower-right side of the editing space, it’s possible to `COPY` the source string to the editor, `CLEAR` the area where translations are typed, and `SUGGEST` or `SAVE` the translation by clicking the corresponding button. This area is also used to [display warnings and errors](translate.md#quality-checks) when submitting a translation.

In the lower-left side:

* Clicking the gear icon allows users to toggle `Translation Toolkit checks` or `Make suggestions`, and navigate to the user settings. Note that access to some settings is restricted by [user permissions](users.md#user-roles).
* Clicking the keyboard icon displays a list of available shortcuts.
* The numbers displayed to the right of the keyboard icon (e.g. `50|59`) are the number of characters in the target and source string.

#### Read-only projects

A project could be enabled in *read-only mode* for some locales: their translations will be available to other languages in the `LOCALES` tab, but it won’t be possible to change or submit translations directly in Pontoon. In this case, a note is displayed in the bar below the editor, and all other controls are hidden.

![Translation editor in read-only project](../assets/localizer/translation-workspace/translation_readonly.png "Screenshot of translation editor in read-only project")

### Translation list

The space below the editor displays the list of [translations](glossary.md#translation) for the current string.

Each entry contains:

* The name of the translator, their profile picture (linking to their profile page) and their banner (see [User banners](#user-banners)).
* How long ago the entry was submitted (hover over to see the full date and time as a tooltip).
* The translation.
* Icons indicating translation status (see below).
* [Translation comments](glossary.md#comment).

Icons to the right indicate the [status](#translation-status) of each translation:

* The solid green circle with checkmark indicates that the translation has been approved.
* The outlined lime green circle with checkmark indicates a pretranslation that has not yet been reviewed.
* If both icons are gray, translation has been suggested but not yet reviewed.
* The red cross indicates that the translation has been rejected. The entire element will look opaque.
* The trashcan, available only for rejected translations, can be used to completely delete a translation. Those with the contributor role can only remove their own translations, while those with a translator permissions can delete anyone’s.

![List of suggestions and translations for a string](../assets/localizer/translation-workspace/translation_comments.png "Screenshot of list of suggestions and translations for a string with comment editing open")

In the screenshot above, the first item is the approved translation (green checkmark), while the other two are rejected suggestions.

#### User banners

User banners provide immediate context about a user to other community members. They indicate either the role of the user, or that the user is new to Pontoon. Banners are displayed at the bottom of the user's avatar.

![Collage of all 5 possible user banners](../assets/localizer/translation-workspace/status_banners.png "Screenshot displaying a collage of all 5 possible user banners that can be displayed")

The available user banners are:

* `MNGR` for [team managers](users.md#user-roles).
* `TRNSL` for [translators](users.md#user-roles).
* `PM` for [project managers](users.md#user-roles).
* `ADMIN` for [administrators](users.md#user-roles).
* `NEW` for users who have joined within the last 3 months.

User banners will also appear in translation comments (see below).

#### Translation comments

By clicking the `COMMENT` button it’s possible to add a **translation comment** to this specific translation. To mention another user in the comment, start typing `@` followed by their name.

If there is already a comment associated with a string, the button will display the number of comments (e.g. `1 COMMENT` for the first rejected suggestion).

#### Viewing translation differences

The `DIFF` option appears if there are multiple translations for one string. Toggling `DIFF` compares the text to the current approved translation, or the most recent suggestion if no translation has been approved yet. Text highlighted in green indicates content that has been added, while strikethrough text in red indicates removed content. Toggling `DIFF` again will display the original string.

![Diff for suggestions](../assets/localizer/translation-workspace/suggestions_diff.png)

## Fluent - FTL files

When working on FTL (Fluent) files, the editing space will look slightly different.

![Translation editing space for Fluent string](../assets/localizer/translation-workspace/editing_space_ftl.png "Screenshot of the translation editing space for Fluent string")

In the example above, the string has a `value` and an attribute `title`. Both are displayed in the source section (highlighted in red), and available as separate input fields in the editor (highlighted in orange).

The following image is an example of a string with plurals: while English only has two forms, plural and singular, other locales can have a different number of plural forms. In this case, Russian has three forms (highlighted in orange).

![Translation editing space for Fluent string with plurals](../assets/localizer/translation-workspace/editing_space_ftl_plurals.png "Screenshot of the translation editing space for Fluent string with plurals")

In the bottom left corner, the FTL button (highlighted in yellow) allows to switch between the standard UI (*Simple FTL mode*) and the *Advanced FTL mode*, where it’s possible to edit the original syntax directly, as you would in a text editor. For details on the Fluent syntax, see [Fluent for localizers](https://mozilla-l10n.github.io/localizer-documentation/tools/fluent/index.html).

![Translation editing space for Fluent string in source view](../assets/localizer/translation-workspace/editing_space_ftl_sourceview.png "Screenshot of the translation editing space for Fluent string in source view")

Note that the FTL button’s text is green when in *Advanced FTL mode*.

## Translation tools and comments

Built-in translation tools are located in the rightmost column.

### Terminology

The `TERMS` tab shows the definition and translation of a term, in case the source string includes matches with the built-in [terminology](glossary.md#terminology). The matching term is also highlighted in the source string. A popup appears on click showing the definition and translation for a term.

![Translation editing space for string with match in terminology](../assets/localizer/translation-workspace/editing_space_terminology.png "Screenshot of the translation editing space for string with match in terminology")

### Source string comments

The `COMMENTS` tab is used to display existing **source string comments**, or add new ones. Source string comments, unlike translation comments, are associated with the string: it’s possible to have a comment in this section even if the string doesn’t have any suggestion or translation yet.

They’re designed for team members to have a conversation about the source string, for example to clarify its meaning, or to get more information from project managers.

Administrators can pin or unpin a source string comment: this pinned comment will be displayed along existing comments in the editing area as `PINNED COMMENT`, and users will [receive a notification](notifications.md#comments).

![Pinned comment](../assets/localizer/translation-workspace/pinned_comment.png "Screenshot of a pinned comment")

The screenshot above shows a pinned comment, and the command to unpin it.

### Machinery

Machinery shows possible translations from a variety of sources. These sources include:

* [Pontoon’s internal translation memory](translate.md#downloading-and-uploading-translations).
* [Google Translate](https://translate.google.com).
* [SYSTRAN](https://www.systran.net/).
* [Caighdean](https://github.com/kscanne/caighdean).
* [Bing Translator](https://www.bing.com/translator) (not currently enabled on pontoon.mozilla.org).

In addition, the user has the ability to search for translations containing words via [`Concordance search`](#concordance-search).

In the tab, the number of entries is visible alongside the `MACHINERY` title in white. If any of the machinery matches are from translation memory, the number of matches will appear separately in green. For example, the screenshot below shows `2+1`, where the green `2` represents the two matches from translation memory and the `1` represents a machinery entry from Google Translate.

![Machinery tab](../assets/localizer/translation-workspace/machinery.png)

At the top of each entry, a diff view compares the current source string and the source string from the machinery entry. Strikethrough text highlighted in red indicates text that is present in the source string but not in the machinery source string, while text highlighted in green indicates text available only in the machinery source string.

To the right of the entry, the number in green shows the percent match between the machinery source string and the current source string. The higher the percentage, the more likely machinery is to be useful; a 100% match indicates that the sources for the current string and for the machinery string are identical.

The origin of the machinery entry is listed in gray above the source string. Clicking the gray text will open the origin in a new window. The green superscript to the right indicates the number of matches for the entry in the translation memory.

Be careful when using the machinery tab as suggestions may not match the source string for the project being translated. Even if the source strings match, the context in which strings are used may not be the same. This could lead to incorrect or unnatural translations. Always keep the meaning and purpose of the string being translated in mind when using the machinery tab.

#### Large language model (LLM) integration

Pontoon will show a dropdown labeled `AI` for all locales that have Google Translate available as a translation source. This feature refines the Google Translate output using an LLM. Opening this dropdown will reveal three options:

* `REPHRASE`: Generate an alternative to this translation.
* `MAKE FORMAL`: Generate a more formal version of this translation.
* `MAKE INFORMAL`: Generate a more informal version of this translation.

![Dropdown to use the LLM feature](../assets/localizer/translation-workspace/llm_dropdown.png "Screenshot of the dropdown to use the LLM feature")

After selecting an option, the revised translation will replace the original suggestion. Once a new translation is generated, another option `SHOW ORIGINAL` will be available in the dropdown menu. Selecting it will revert to the original suggestion.

![Enhanced translation output from the LLM rephrasing the initial Google Translate result.](../assets/localizer/translation-workspace/llm_dropdown_rephrased.png "Screenshot of enhanced translation output from the LLM rephrasing the initial Google Translate result.")

#### Concordance search

Concordance search allows users to search across all projects in Pontoon. Users can search for translations using strings in either source or target language. Matching results are displayed with the source string, translation, and project name; clicking a result will automatically fill the translation into the editor. Note that the search does not need to be related to the current string or project.

![Concordance search](../assets/localizer/translation-workspace/concordance_search.png)

### Locales

The locales tab shows approved translations from Pontoon projects in other [locales](glossary.md#locale).

![Locales tab](../assets/localizer/translation-workspace/locales.png)

Next to the `LOCALES` title, the number of available entries is visible. The number for preferred locales is green, while the number for all other locales is in gray.

Users can select locales to appear at the top of their Locales tab as a preferred locale. To add a locale to the preferred locale list, access the [user settings](users.md#locale-settings) page.

Entries in the `LOCALES` tab above the green line are preferred locales. Non-preferred locales are displayed below the green line, sorted alphabetically by language name.

Each row displays the translation for the source string in the selected locale. Above each entry, the language name is visible in gray, while the locale code is displayed in green.

The `LOCALES` tab is useful for seeing what general style choices are made by other localization communities. When encountering a difficult string, a translator can use other locales as a source of inspiration.

Note that, when using the `LOCALES` tab, the translator should always opt for fluency in their own locale. Languages vary linguistically on many levels. The locales tab can be extremely useful, but should be used carefully, and rarely as the sole translation resource for translation.

## Smaller screens

The translation workspace is responsive, which means the layout will adapt to smaller screens. Everything you do on your desktop computer or laptop, you can also do on your phone or tablet: review strings, fix typos or even translate a few strings on the go.

![Mobile UI](../assets/localizer/translation-workspace/mobile_ui.png "Screenshot of the mobile UI")
