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

batchactions-RejectAll--default = Reject all
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


## Editor Menu
## Allows contributors to modify or propose a translation

editor-EditorMenu--sign-in-to-translate = <a>Sign in</a> to translate.
editor-EditorMenu--read-only-localization = This is a read-only localization.
editor-EditorMenu--button-copy = Copy
editor-EditorMenu--button-clear = Clear
editor-EditorMenu--button-save = Save
editor-EditorMenu--button-suggest = Suggest


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

editor-KeyboardShortcuts--copy-from-helpers = Copy From Helpers
editor-KeyboardShortcuts--copy-from-helpers-shortcut = <accel>Tab</accel>


## Editor Unsaved Changes
## Renders the unsaved changes popup

editor-UnsavedChanges--close = ×
    .aria-label = Close unsaved changes popup
editor-UnsavedChanges--title = You have unsaved changes
editor-UnsavedChanges--body = Sure you want to leave?
editor-UnsavedChanges--leave-anyway = Leave anyway


## Entity Details Navigation
## Shows next/previous buttons.

entitydetails-EntityNavigation--next = <glyph></glyph>Next
    .title = Go To Next String (Alt + Down)
entitydetails-EntityNavigation--previous = <glyph></glyph>Previous
    .title = Go To Previous String (Alt + Up)


## Entity Details Helpers
## Shows helper tabs

entitydetails-Helpers--history = History
entitydetails-Helpers--machinery = Machinery
entitydetails-Helpers--locales = Locales


## Entity Details Metadata
## Shows metadata about an entity (original string)

entitydetails-Metadata--comment =
    .title = Comment

entitydetails-Metadata--context =
    .title = Context

entitydetails-Metadata--placeholder =
    .title = Placeholder Examples

entitydetails-Metadata--resource =
    .title = Resource

entitydetails-Metadata--project =
    .title = Project


## Entity Details GenericOriginalString
## Shows the original string of an entity

entitydetails-GenericOriginalString--plural = Plural
entitydetails-GenericOriginalString--singular = Singular


## History
## Shows a list of translations for a specific entity

history-History--no-translations = No translations available.


## History Translation
## Shows a specific translation for an entity, and actions around it

history-Translation--copy =
    .title = Copy Into Translation (Tab)

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


## Machinery
## Shows a list of translations from machines.

machinery-Machinery--search-placeholder =
    .placeholder = Type to search machinery


## Machinery Translation
## Shows a specific translation from machinery

machinery-Translation--copy =
    .title = Copy Into Translation (Tab)

machinery-Translation--number-occurrences =
    .title = Number of translation occurrences


## Notification Messages
## Messages shown to users after they perform actions.

notification--translation-approved = Translation approved
notification--translation-unaproved = Translation unaproved
notification--translation-rejected = Translation rejected
notification--translation-unrejected = Translation unrejected
notification--translation-deleted = Translation deleted
notification--translation-added = Translation added
notification--translation-saved = Translation saved
notification--translation-updated = Translation updated
notification--unable-to-approve-translation = Unable to approve translation
notification--unable-to-unapprove-translation = Unable to unapprove translation
notification--unable-to-reject-translation = Unable to reject translation
notification--unable-to-unreject-translation = Unable to unreject translation
notification--same-translation = Same translation already exists
notification--tt-checks-enabled = Translate Toolkit Checks enabled
notification--tt-checks-disabled = Translate Toolkit Checks disabled
notification--make-suggestions-enabled = Make Suggestions enabled
notification--make-suggestions-disabled = Make Suggestions disabled
notification--entity-not-found = Can’t load specified string


## OtherLocales Translation
## Shows a specific translation from a different locale

otherlocales-Translation--copy =
    .title = Copy Into Translation (Tab)


## Placeable parsers
## Used to mark specific terms and characters in translations.

placeable-parser-allCapitalsString =
    .title = Long all-caps string
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


## Resource menu
## Used in the resource menu in the main navigation bar.
resource-ResourceMenu--no-results = No results
resource-ResourceMenu--all-resources = All Resources
resource-ResourceMenu--all-projects = All Projects


## Search
## The search bar and filters menu.

search-FiltersPanel--heading-status = Translation Status
search-FiltersPanel--heading-tags = Tags
search-FiltersPanel--heading-extra = Extra Filters
search-FiltersPanel--heading-authors = Translation Authors

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


## User Menu
## Shows user menu entries and options to sign in or out.

user-AppSwitcher--leave-translate-next = Leave Translate.Next
user-SignIn--sign-in = Sign in
user-SignOut--sign-out = <glyph></glyph>Sign out

user-UserMenu--download-tm = <glyph></glyph>Download Translation Memory
user-UserMenu--download-translations = <glyph></glyph>Download Translations
user-UserMenu--upload-translations = <glyph></glyph>Upload Translations

user-UserMenu--top-contributors = <glyph></glyph>Top Contributors
user-UserMenu--machinery = <glyph></glyph>Machinery
user-UserMenu--terms = <glyph></glyph>Terms of Use
user-UserMenu--help = <glyph></glyph>Help

user-UserMenu--admin = <glyph></glyph>Admin
user-UserMenu--admin-project = <glyph></glyph>Admin · Current Project

user-UserMenu--settings = <glyph></glyph>Settings


## User Notifications
## Shows user notifications menu.

user-UserNotificationsMenu--no-notifications-title = No new notifications.
user-UserNotificationsMenu--no-notifications-description = Here you’ll see updates for localizations you contribute to.
user-UserNotificationsMenu--see-all-notifications = See all Notifications
