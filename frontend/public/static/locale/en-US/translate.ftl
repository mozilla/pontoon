### Localization for the Translate page of Pontoon

# Naming convention for l10n IDs: "module-ComponentName--string-summary".
# This allows us to minimize the risk of conflicting IDs throughout the app.
# Please sort alphabetically by (module name, component name). For each module,
# keep strings in order of appearance.


## ApproveAll
## Renders Approve All batch action button.

batchactions-ApproveAll--default = Approve all
batchactions-ApproveAll--success =
    { $changedCount ->
        [one] { $changedCount } string approved
       *[other] { $changedCount } strings approved
    }
batchactions-ApproveAll--invalid = { $invalidCount } failed
batchactions-ApproveAll--error = Oops, something went wrong


## BatchActions
## Renders batch editor, used for performing mass actions on translations.

batchactions-BatchActions--header-selected-count =
    { $count ->
        [one] <glyph></glyph> <stress>{ $count }</stress> string selected
       *[other] <glyph></glyph> <stress>{ $count }</stress> strings selected
    }
    .title = Quit Batch Editing (Esc)
batchactions-BatchActions--header-select-all = <glyph></glyph> Select All
    .title = Select All Strings (Ctrl + Shift + A)

batchactions-BatchActions--warning = <stress>Warning:</stress> These actions will be applied to all selected strings and cannot be undone.

batchactions-BatchActions--review-heading = Review translations

batchactions-BatchActions--find-replace-heading = Find & Replace in translations
batchactions-BatchActions--find =
    .placeholder = Find
batchactions-BatchActions--replace-with =
    .placeholder = Replace with


## RejectAll
## Renders Reject All batch action button.

batchactions-RejectAll--default = Reject all suggestions
batchactions-RejectAll--confirmation = Are you sure?
batchactions-RejectAll--success =
    { $changedCount ->
        [one] { $changedCount } string rejected
       *[other] { $changedCount } strings rejected
    }
batchactions-RejectAll--invalid = { $invalidCount } failed
batchactions-RejectAll--error = Oops, something went wrong


## ReplaceAll
## Renders Replace All batch action button.

batchactions-ReplaceAll--default = Replace all
batchactions-ReplaceAll--success =
    { $changedCount ->
        [one] { $changedCount } string replaced
       *[other] { $changedCount } strings replaced
    }
batchactions-ReplaceAll--invalid = { $invalidCount } failed
batchactions-ReplaceAll--error = Oops, something went wrong


## ResourceProgress
##  Show a panel with progress chart and stats for the current resource.

resourceprogress-ResourceProgress--all-strings = All strings
resourceprogress-ResourceProgress--unreviewed = Unreviewed
resourceprogress-ResourceProgress--translated = Translated
resourceprogress-ResourceProgress--fuzzy = Fuzzy
resourceprogress-ResourceProgress--warnings = Warnings
resourceprogress-ResourceProgress--errors = Errors
resourceprogress-ResourceProgress--missing = Missing


## Comments
## Allows user to leave comments on translations

comments-AddComment--input =
    .placeholder = Write a comment…
comments-AddComment--mention-avatar-alt = 
    .alt = User Avatar 
comments-AddComment--submit-button = <glyph></glyph>
    .title = Submit comment
comments-Comment--pin-button = PIN
    .title = Pin comment
comments-Comment--unpin-button = UNPIN
    .title = Unpin comment


## Editor Menu
## Allows contributors to modify or propose a translation

editor-EditorMenu--sign-in-to-translate = <a>Sign in</a> to translate.
editor-EditorMenu--read-only-localization = This is a read-only localization.
editor-EditorMenu--button-copy = Copy
    .title = Copy From Source (Ctrl + Shift + C)
editor-EditorMenu--button-clear = Clear
    .title = Clear Translation (Ctrl + Shift + Backspace)
editor-EditorMenu--button-approve = Approve
    .title = Approve Translation (Enter)
editor-EditorMenu--button-approving = <glyph></glyph>Approving
    .title = Approving Translation…
editor-EditorMenu--button-save = Save
    .title = Save Translation (Enter)
editor-EditorMenu--button-saving = <glyph></glyph>Saving
    .title = Saving Translation…
editor-EditorMenu--button-suggest = Suggest
    .title = Suggest Translation (Enter)
editor-EditorMenu--button-suggesting = <glyph></glyph>Suggesting
    .title = Suggesting Translation…


## Editor Settings
## Shows options to update user settings regarding the editor.

editor-EditorSettings--toolkit-checks = <glyph></glyph>Translate Toolkit Checks
    .title = Run Translate Toolkit checks before submitting translations

editor-EditorSettings--force-suggestions = <glyph></glyph>Make Suggestions
    .title = Save suggestions instead of translations

editor-EditorSettings--change-all = Change All Settings


## Editor Failed Checks
## Renders the failed checks popup

editor-FailedChecks--close = ×
    .aria-label = Close failed checks popup
editor-FailedChecks--title = The following checks have failed
editor-FailedChecks--save-anyway = Save anyway
editor-FailedChecks--suggest-anyway = Suggest anyway
editor-FailedChecks--approve-anyway = Approve anyway


## Editor Keyboard Shortcuts
## Shows a list of keyboard shortcuts.

editor-KeyboardShortcuts--button =
    .title = Keyboard Shortcuts

editor-KeyboardShortcuts--overlay-title = Keyboard Shortcuts

editor-KeyboardShortcuts--save-translation = Save Translation
editor-KeyboardShortcuts--save-translation-shortcut = <accel>Enter</accel>

editor-KeyboardShortcuts--cancel-translation = Cancel Translation
editor-KeyboardShortcuts--cancel-translation-shortcut = <accel>Esc</accel>

editor-KeyboardShortcuts--insert-a-new-line = Insert A New Line
editor-KeyboardShortcuts--insert-a-new-line-shortcut = <mod1>Shift</mod1> + <accel>Enter</accel>

editor-KeyboardShortcuts--go-to-next-string = Go To Next String
editor-KeyboardShortcuts--go-to-next-string-shortcut = <mod1>Alt</mod1> + <accel>Down</accel>

editor-KeyboardShortcuts--go-to-previous-string = Go To Previous String
editor-KeyboardShortcuts--go-to-previous-string-shortcut = <mod1>Alt</mod1> + <accel>Up</accel>

editor-KeyboardShortcuts--copy-from-source = Copy From Source
editor-KeyboardShortcuts--copy-from-source-shortcut = <mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>C</accel>

editor-KeyboardShortcuts--clear-translation = Clear Translation
editor-KeyboardShortcuts--clear-translation-shortcut = <mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>Backspace</accel>

editor-KeyboardShortcuts--search-strings = Search Strings
editor-KeyboardShortcuts--search-strings-shortcut = <mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>F</accel>

editor-KeyboardShortcuts--select-all-strings = Select All Strings
editor-KeyboardShortcuts--select-all-strings-shortcut = <mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>A</accel>


## Editor Unsaved Changes
## Renders the unsaved changes popup

editor-UnsavedChanges--close = ×
    .aria-label = Close unsaved changes popup
editor-UnsavedChanges--title = You have unsaved changes
editor-UnsavedChanges--body = Are you sure you want to proceed?
editor-UnsavedChanges--proceed = Proceed


## Entity Details Navigation
## Shows Copy Link and Next/Previous buttons.

entitydetails-EntityNavigation--link = <glyph></glyph>Copy Link
    .title = Copy Link to String
entitydetails-EntityNavigation--next = <glyph></glyph>Next
    .title = Go To Next String (Alt + Down)
entitydetails-EntityNavigation--previous = <glyph></glyph>Previous
    .title = Go To Previous String (Alt + Up)


## Entity Details Helpers
## Shows helper tabs

entitydetails-Helpers--terms = Terms
entitydetails-Helpers--no-terms = No terms available.

entitydetails-Helpers--comments = Comments
entitydetails-Helpers--no-comments = No comments available.

entitydetails-Helpers--machinery = Machinery
entitydetails-Helpers--locales = Locales

## Entity Details Metadata
## Shows metadata about an entity (original string)

entitydetails-Metadata--comment =
    .title = Comment

entitydetails-Metadata--group-comment =
    .title = Group Comment

entitydetails-Metadata--resource-comment =
    .title = Resource Comment

entitydetails-Metadata--pinned-comment =
    .title = Pinned Comment

entitydetails-Metadata--see-more = See More

entitydetails-Metadata--context =
    .title = Context

entitydetails-Metadata--placeholder =
    .title = Placeholder Examples

entitydetails-Metadata--resource =
    .title = Resource


## Entity Details GenericOriginalString
## Shows the original string of an entity

entitydetails-GenericOriginalString--plural = Plural
entitydetails-GenericOriginalString--singular = Singular


## Rich editor
## Renders a Rich editor for Fluent string editing

fluenteditor-RichTranslationForm--plural-example = { $plural } (e.g. <stress>{ $example }</stress>)


## History
## Shows a list of translations for a specific entity

history-History--no-translations = No translations available.


## History Translation
## Shows a specific translation for an entity, and actions around it

history-Translation--copy =
    .title = Copy Into Translation

history-Translation--hide-diff = Hide diff
    .title = Hide diff against the currently active translation
history-Translation--show-diff = Show diff
    .title = Show diff against the currently active translation

history-Translation--button-delete =
    .title = Delete

history-Translation--button-approve =
    .title = Approve

history-Translation--button-unapprove =
    .title = Unapprove

history-Translation--button-reject =
    .title = Reject

history-Translation--button-unreject =
    .title = Unreject

history-Translation--button-not-approved =
    .title = Not approved

history-Translation--button-approved =
    .title = Approved

history-Translation--button-not-rejected =
    .title = Not rejected

history-Translation--button-rejected =
    .title = Rejected

history-Translation--button-comment = Comment
    .title = Toggle translation comments

history-Translation--button-comments = { $commentCount ->
        [one] <stress>{ $commentCount }</stress> Comment
       *[other] <stress>{ $commentCount }</stress> Comments
    }
    .title = Toggle translation comments

history-Translation--span-copied =
    .title = Copied ({ $machinerySources })

## Interactive Tour
## Shows an interactive Tour on the "Tutorial" project,
## introducing the translate page of Pontoon.

interactivetour-InteractiveTour--intro-title = Hey there!
interactivetour-InteractiveTour--intro-content =
    Pontoon is a localization platform by Mozilla, used to localize
    Firefox and various other projects at Mozilla and other organizations.
interactivetour-InteractiveTour--intro-footer = Follow this guide to learn how to use it.

interactivetour-InteractiveTour--main-toolbar-title = Main toolbar
interactivetour-InteractiveTour--main-toolbar-content =
    The main toolbar located on top of the screen shows the language,
    project and resource currently being localized. You can also
    see the progress of your current localization and additional
    project information.
interactivetour-InteractiveTour--main-toolbar-footer =
    On the right hand side, logged in users can access notifications
    and settings.

interactivetour-InteractiveTour--string-list-title = String List
interactivetour-InteractiveTour--string-list-content =
    The sidebar displays a list of strings in the current
    localization. Status of each string (e.g. Translated or Missing)
    is indicated by a different color of the square on the left. The
    square also acts as a checkbox for selecting strings to perform
    mass actions on.
interactivetour-InteractiveTour--string-list-footer =
    On top of the list is a search box, which allows you to
    search source strings, translations, comments and string IDs.

interactivetour-InteractiveTour--filters-title = Filters
interactivetour-InteractiveTour--filters-content =
    Strings can also be filtered by their status, translation time,
    translation authors and other criteria. Note that filter icons act
    as checkboxes, which allows you to filter by multiple criteria.

interactivetour-InteractiveTour--editor-title = Editor
interactivetour-InteractiveTour--editor-content =
    Clicking a string in the list opens it in the editor. On top of
    it, you can see the source string with its context. Right under
    that is the translation input to type translation in, followed
    by the translation toolbar.

interactivetour-InteractiveTour--submit-title = Submit a Translation
interactivetour-InteractiveTour--submit-content-unauthenticated =
    A user needs to be logged in to be able to submit translations.
    Non-authenticated users will see a link to Sign in instead of the
    translation toolbar with a button to save translations.
interactivetour-InteractiveTour--submit-content-contributor =
    When a translator is in Suggest Mode, or doesn’t have permission
    to submit translations directly, a blue SUGGEST button will appear
    in the translation toolbar. To make a suggestion, type it in the
    translation input and click SUGGEST.
interactivetour-InteractiveTour--submit-content-translator =
    If a translator has permission to add translations directly,
    the green SAVE button will appear in the translation toolbar.
    To submit a translation, type it in the translation input and
    click SAVE.

interactivetour-InteractiveTour--history-title = History
interactivetour-InteractiveTour--history-content =
    All suggestions and translations submitted for the current
    string can be found in the History Tab. Icons to the right of
    each entry indicate its review status (Approved, Rejected or
    Unreviewed).

interactivetour-InteractiveTour--machinery-title = Machinery
interactivetour-InteractiveTour--machinery-content =
    The Machinery tab shows automated translation suggestions from
    Machine Translation, Translation Memory and Terminology services.
    Clicking on an entry copies it to the translation input.

interactivetour-InteractiveTour--locales-title = Locales
interactivetour-InteractiveTour--locales-content =
    Sometimes it’s useful to see general style choices by other
    localization communities. Approved translations of the current
    string to other languages are available in the Locales tab.

interactivetour-InteractiveTour--end-title = That’s (not) all, folks!
interactivetour-InteractiveTour--end-content =
    There’s a wide variety of tools to help you with translations,
    some of which we didn’t mention in this tutorial. For more
    topics of interest for localizers at Mozilla, please have a look
    at the <a>Localizer Documentation</a>.
interactivetour-InteractiveTour--end-footer =
    Next, feel free to explore this tutorial project or move straight
    to <a>translating live projects</a>.


## Machinery
## Shows a list of translations from machines.
machinery-Machinery--search-placeholder =
    .placeholder = Search in Machinery


## Machinery Caighdean Translation
## Shows the translation source from Caighdean Machine Translation.
machinery-CaighdeanTranslation--visit-caighdean = Caighdean
    .title = Visit Caighdean Machine Translation


## Machinery Google Translation
## Shows the translation source from Google Translate.
machinery-GoogleTranslation--visit-google = Google Translate
    .title = Visit Google Translate


## Machinery Microsoft Translation
## Shows the translation source from Microsoft Translation.
machinery-MicrosoftTranslation--visit-bing = Microsoft Translator
    .title = Visit Microsoft Translator


## Machinery Systran Translate
## Shows the translation source from Systran Translate.
machinery-SystranTranslate--visit-systran = Systran Translate
    .title = Visit Systran Translate


## Machinery Microsoft Terminology
## Shows the translation source from Microsoft Terminology.
machinery-MicrosoftTerminology--visit-microsoft = Microsoft
    .title =
        Visit Microsoft Terminology Service API.
        © 2018 Microsoft Corporation. All rights reserved.


## Machinery Translation
## Shows a specific translation from machinery.
machinery-Translation--copy =
    .title = Copy Into Translation


## Machinery Translation Memory
## Shows the translation source from Pontoon's memory.
machinery-TranslationMemory--pontoon-homepage =
    .title = Pontoon Homepage
machinery-TranslationMemory--translation-memory = Translation memory
machinery-TranslationMemory--number-occurrences =
    .title = Number of translation occurrences


## Machinery Transvision Memory
## Shows the translation source from Transvision.
machinery-TransvisionMemory--visit-transvision = Mozilla
    .title = Visit Transvision


## Notification Messages
## Messages shown to users after they perform actions.

notification--translation-approved = Translation approved
notification--translation-unaproved = Translation unaproved
notification--translation-rejected = Translation rejected
notification--translation-unrejected = Translation unrejected
notification--translation-deleted = Translation deleted
notification--translation-saved = Translation saved
notification--unable-to-approve-translation = Unable to approve translation
notification--unable-to-unapprove-translation = Unable to unapprove translation
notification--unable-to-reject-translation = Unable to reject translation
notification--unable-to-unreject-translation = Unable to unreject translation
notification--unable-to-delete-translation = Unable to delete translation
notification--same-translation = Same translation already exists
notification--tt-checks-enabled = Translate Toolkit Checks enabled
notification--tt-checks-disabled = Translate Toolkit Checks disabled
notification--make-suggestions-enabled = Make Suggestions enabled
notification--make-suggestions-disabled = Make Suggestions disabled
notification--entity-not-found = Can’t load specified string
notification--string-link-copied = Link copied to clipboard
notification--comment-added = Comment added


## OtherLocales Translation
## Shows a specific translation from a different locale

otherlocales-Translation--copy =
    .title = Copy Into Translation

otherlocales-Translation--header-link =
    .title = Open string in { $locale } ({ $code })


## Placeable parsers
## Used to mark specific terms and characters in translations.

placeable-parser-altAttribute =
    .title = 'alt' attribute inside XML tag
placeable-parser-camelCaseString =
    .title = Camel case string
placeable-parser-emailPattern =
    .title = Email
placeable-parser-escapeSequence =
    .title = Escape sequence
placeable-parser-filePattern =
    .title = File location
placeable-parser-javaFormattingVariable =
    .title = Java Message formatting variable
placeable-parser-jsonPlaceholder =
    .title = JSON placeholder
placeable-parser-multipleSpaces =
    .title = Multiple spaces
placeable-parser-narrowNonBreakingSpace =
    .title = Narrow non-breaking space
placeable-parser-newlineCharacter =
    .title = Newline character
placeable-parser-newlineEscape =
    .title = Escaped newline
placeable-parser-nonBreakingSpace =
    .title = Non-breaking space
placeable-parser-nsisVariable =
    .title = NSIS Variable
placeable-parser-numberString =
    .title = Number
placeable-parser-optionPattern =
    .title = Command line option
placeable-parser-punctuation =
    .title = Punctuation
placeable-parser-pythonFormatNamedString =
    .title = Python format string
placeable-parser-pythonFormatString =
    .title = Python format string
placeable-parser-pythonFormattingVariable =
    .title = Python string formatting variable
placeable-parser-qtFormatting =
    .title = Qt string formatting variable
placeable-parser-stringFormattingVariable =
    .title = String formatting variable
placeable-parser-shortCapitalNumberString =
    .title = Short capital letter and number string
placeable-parser-tabCharacter =
    .title = Tab character
placeable-parser-thinSpace =
    .title = Thin space
placeable-parser-unusualSpace =
    .title = Unusual space in string
placeable-parser-uriPattern =
    .title = URI
placeable-parser-xmlEntity =
    .title = XML entity
placeable-parser-xmlTag =
    .title = XML tag


## Project menu
## Used in the project menu in the main navigation bar.
project-ProjectMenu--no-results = No results
project-ProjectMenu--project = Project
project-ProjectMenu--progress = Progress
project-ProjectMenu--all-projects = All Projects
project-ProjectMenu--search-placeholder =
    .placeholder = Filter projects


## Resource menu
## Used in the resource menu in the main navigation bar.
resource-ResourceMenu--no-results = No results
resource-ResourceMenu--resource = Resource
resource-ResourceMenu--progress = Progress
resource-ResourceMenu--all-resources = All Resources
resource-ResourceMenu--all-projects = All Projects
resource-ResourceMenu--search-placeholder =
    .placeholder = Filter resources


## Filters Panel
## Shows a list of filters, used to filter the list of entities.
search-FiltersPanel--heading-status = Translation Status
search-FiltersPanel--heading-tags = Tags
search-FiltersPanel--heading-extra = Extra Filters
search-FiltersPanel--heading-authors = Translation Authors
search-FiltersPanel--status-name-all = All
search-FiltersPanel--status-name-translated = Translated
search-FiltersPanel--status-name-fuzzy = Fuzzy
search-FiltersPanel--status-name-warnings = Warnings
search-FiltersPanel--status-name-errors = Errors
search-FiltersPanel--status-name-missing = Missing
search-FiltersPanel--status-name-unreviewed = Unreviewed
search-FiltersPanel--extra-name-unchanged = Unchanged
search-FiltersPanel--extra-name-empty = Empty
search-FiltersPanel--extra-name-rejected = Rejected

search-FiltersPanel--clear-selection = <glyph></glyph>Clear
    .title = Uncheck selected filters

search-FiltersPanel--apply-filters =
    <glyph></glyph>Apply <stress>{ $count }</stress> { $count ->
        [one] filter
       *[other] filters
    }
    .title = Apply Selected Filters


## Time Range Filter
## Time Range filter title, input fields and chart.

search-TimeRangeFilter--heading-time = Translation Time
search-TimeRangeFilter--edit-range = <glyph></glyph>Edit Range
search-TimeRangeFilter--save-range = Save Range


## Term
## Shows term entry with its metadata

term-Term--for-example = E.g.


## User Avatar
## Shows user Avatar with alt text

user-UserAvatar--anon-alt-text = 
    .alt = Anonymous User
user-UserAvatar--alt-text = 
    .alt = User Profile

## User Menu
## Shows user menu entries and options to sign in or out.

user-SignIn--sign-in = Sign in
user-SignOut--sign-out = <glyph></glyph>Sign out

user-UserMenu--download-terminology = <glyph></glyph>Download Terminology
user-UserMenu--download-tm = <glyph></glyph>Download Translation Memory
user-UserMenu--download-translations = <glyph></glyph>Download Translations
user-UserMenu--upload-translations = <glyph></glyph>Upload Translations

user-UserMenu--terms = <glyph></glyph>Terms of Use
user-UserMenu--github = <glyph></glyph>Hack it on GitHub
user-UserMenu--feedback = <glyph></glyph>Give Feedback
user-UserMenu--help = <glyph></glyph>Help

user-UserMenu--admin = <glyph></glyph>Admin
user-UserMenu--admin-project = <glyph></glyph>Admin · Current Project

user-UserMenu--settings = <glyph></glyph>Settings


## User Notifications
## Shows user notifications menu.

user-UserNotificationsMenu--no-notifications-title = No new notifications.
user-UserNotificationsMenu--no-notifications-description = Here you’ll see updates for localizations you contribute to.
user-UserNotificationsMenu--see-all-notifications = See all Notifications


## Project Info
## Shows information of all projects

projectinfo-ProjectInfo--project-info-title = Project Info
