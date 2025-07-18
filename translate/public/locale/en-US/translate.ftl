### Localization for the Translate page of Pontoon


## Pontoon Add-On promotion
## Renders Pontoon Add-On promotion banner

addonpromotion-AddonPromotion--dismiss = ×
    .aria-label = Dismiss
addonpromotion-AddonPromotion--get = Get Pontoon Add-On
addonpromotion-AddonPromotion--text = Take your Pontoon notifications everywhere with the official Pontoon Add-on.


## ApproveAll
## Renders Approve All batch action button.

batchactions-ApproveAll--default = APPROVE ALL
batchactions-ApproveAll--success =
    { $changedCount ->
        [one] { $changedCount } STRING APPROVED
       *[other] { $changedCount } STRINGS APPROVED
    }
batchactions-ApproveAll--invalid = { $invalidCount } FAILED
batchactions-ApproveAll--error = OOPS, SOMETHING WENT WRONG


## BatchActions
## Renders batch editor, used for performing mass actions on translations.

batchactions-BatchActions--header-selected-count =
    { $count ->
        [one] <glyph></glyph> <stress>{ $count }</stress> STRING SELECTED
       *[other] <glyph></glyph> <stress>{ $count }</stress> STRINGS SELECTED
    }
    .title = Quit Batch Editing (Esc)
batchactions-BatchActions--header-select-all = <glyph></glyph> SELECT ALL
    .title = Select All Strings (Ctrl + Shift + A)

batchactions-BatchActions--warning = <stress>Warning:</stress> These actions will be applied to all selected strings and cannot be undone.

batchactions-BatchActions--review-heading = REVIEW TRANSLATIONS

batchactions-BatchActions--find-replace-heading = FIND & REPLACE IN TRANSLATIONS
batchactions-BatchActions--find =
    .placeholder = Find
batchactions-BatchActions--replace-with =
    .placeholder = Replace with


## RejectAll
## Renders Reject All batch action button.

batchactions-RejectAll--default = REJECT ALL SUGGESTIONS
batchactions-RejectAll--confirmation = ARE YOU SURE?
batchactions-RejectAll--success =
    { $changedCount ->
        [one] { $changedCount } STRING REJECTED
       *[other] { $changedCount } STRINGS REJECTED
    }
batchactions-RejectAll--invalid = { $invalidCount } FAILED
batchactions-RejectAll--error = OOPS, SOMETHING WENT WRONG


## ReplaceAll
## Renders Replace All batch action button.

batchactions-ReplaceAll--default = REPLACE ALL
batchactions-ReplaceAll--success =
    { $changedCount ->
        [one] { $changedCount } STRING REPLACED
       *[other] { $changedCount } STRINGS REPLACED
    }
batchactions-ReplaceAll--invalid = { $invalidCount } FAILED
batchactions-ReplaceAll--error = OOPS, SOMETHING WENT WRONG


## ResourceProgress
##  Show a panel with progress chart and stats for the current resource.

resourceprogress-ResourceProgress--all-strings = ALL STRINGS
resourceprogress-ResourceProgress--unreviewed = UNREVIEWED
resourceprogress-ResourceProgress--translated = TRANSLATED
resourceprogress-ResourceProgress--pretranslated = PRETRANSLATED
resourceprogress-ResourceProgress--warnings = WARNINGS
resourceprogress-ResourceProgress--errors = ERRORS
resourceprogress-ResourceProgress--missing = MISSING


## Comments
## Allows user to leave comments on translations and source strings

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
comments-Comment--pinned = PINNED
comments-CommentsList--pinned-comments = PINNED COMMENTS
comments-CommentsList--all-comments = ALL COMMENTS


## Editor Menu
## Allows contributors to modify or propose a translation

editor-EditorMenu--sign-in-to-translate = <form>Sign in</form> to translate.
editor-EditorMenu--read-only-localization = This is a read-only localization.
editor-EditorMenu--button-copy = COPY
    .title = Copy From Source (Ctrl + Shift + C)
editor-EditorMenu--button-clear = CLEAR
    .title = Clear Translation (Ctrl + Shift + Backspace)
editor-EditorMenu--button-approve = APPROVE
    .title = Approve Translation (Enter)
editor-EditorMenu--button-approving = <glyph></glyph>APPROVING
    .title = Approving Translation…
editor-EditorMenu--button-save = SAVE
    .title = Save Translation (Enter)
editor-EditorMenu--button-saving = <glyph></glyph>SAVING
    .title = Saving Translation…
editor-EditorMenu--button-suggest = SUGGEST
    .title = Suggest Translation (Enter)
editor-EditorMenu--button-suggesting = <glyph></glyph>SUGGESTING
    .title = Suggesting Translation…


## Editor Settings
## Shows options to update user settings regarding the editor.

editor-EditorSettings--toolkit-checks = <glyph></glyph>Translate Toolkit checks
    .title = Run Translate Toolkit checks before submitting translations

editor-EditorSettings--force-suggestions = <glyph></glyph>Make suggestions
    .title = Save suggestions instead of translations

editor-EditorSettings--change-all = Change all settings


## Editor FTL Source Editor Switch
## A button that allows switching the editor to/from FTL source mode.

editor-FtlSwitch--toggle =
    .title = Toggle between simple and advanced FTL mode

editor-FtlSwitch--active =
    .title = Advanced FTL mode enabled


## Editor Failed Checks
## Renders the failed checks popup

editor-FailedChecks--close = ×
    .aria-label = Close failed checks popup
editor-FailedChecks--title = THE FOLLOWING CHECKS HAVE FAILED
editor-FailedChecks--save-anyway = SAVE ANYWAY
editor-FailedChecks--suggest-anyway = SUGGEST ANYWAY
editor-FailedChecks--approve-anyway = APPROVE ANYWAY


## Editor Keyboard Shortcuts
## Shows a list of keyboard shortcuts.

editor-KeyboardShortcuts--button =
    .title = Keyboard Shortcuts

editor-KeyboardShortcuts--overlay-title = KEYBOARD SHORTCUTS

editor-KeyboardShortcuts--save-translation = Save Translation
editor-KeyboardShortcuts--save-translation-shortcut = <accel>Enter</accel>

editor-KeyboardShortcuts--cancel-translation = Cancel Translation
editor-KeyboardShortcuts--cancel-translation-shortcut = <accel>Esc</accel>

editor-KeyboardShortcuts--insert-a-new-line = Insert A New Line
editor-KeyboardShortcuts--insert-a-new-line-shortcut = <mod1>Shift</mod1> + <accel>Enter</accel>

editor-KeyboardShortcuts--go-to-previous-string = Go To Previous String
editor-KeyboardShortcuts--go-to-previous-string-shortcut = <mod1>Alt</mod1> + <accel>Up</accel>

editor-KeyboardShortcuts--go-to-next-string = Go To Next String
editor-KeyboardShortcuts--go-to-next-string-shortcut = <mod1>Alt</mod1> + <accel>Down</accel>

editor-KeyboardShortcuts--copy-from-source = Copy From Source
editor-KeyboardShortcuts--copy-from-source-shortcut = <mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>C</accel>

editor-KeyboardShortcuts--clear-translation = Clear Translation
editor-KeyboardShortcuts--clear-translation-shortcut = <mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>Backspace</accel>

editor-KeyboardShortcuts--search-strings = Search Strings
editor-KeyboardShortcuts--search-strings-shortcut = <mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>F</accel>

editor-KeyboardShortcuts--select-all-strings = Select All Strings
editor-KeyboardShortcuts--select-all-strings-shortcut = <mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>A</accel>

editor-KeyboardShortcuts--copy-from-previous-helper = Copy From Previous Helper
editor-KeyboardShortcuts--copy-from-previous-helper-shortcut = <mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>Up</accel>

editor-KeyboardShortcuts--copy-from-next-helper = Copy From Next Helper
editor-KeyboardShortcuts--copy-from-next-helper-shortcut = <mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>Down</accel>


## Editor machinery source indicator
## Shown when a perfect match is provided automatically from translation memory

editor-MachinerySourceIndicator--text = <stress>100%</stress> MATCH FROM TRANSLATION MEMORY


## Editor New Contributor Tooltip
## Renders the guidelines for new contributors

editor-NewContributorTooltip--intro = It looks like you haven’t contributed to this locale yet.
editor-NewContributorTooltip--team-info = Check the <a>team information</a> before starting, as it might contain important information and language resources.
editor-NewContributorTooltip--team-managers = Reach out to <a>team managers</a> if you have questions or want to learn more about contributing.


## Editor Badge Tooltip
## Popup notification when users gain a new badge level

editor-BadgeTooltip--intro = Achievement unlocked
editor-BadgeTooltip--level = Level { $badgeLevel }
editor-BadgeTooltip--profile = View your new badge in your <a>profile</a>.
editor-BadgeTooltip--continue = Continue


## Editor Unsaved Changes
## Renders the unsaved changes popup

editor-UnsavedChanges--close = ×
    .aria-label = Close unsaved changes popup
editor-UnsavedChanges--title = YOU HAVE UNSAVED CHANGES
editor-UnsavedChanges--body = Are you sure you want to proceed?
editor-UnsavedChanges--proceed = PROCEED


## Entity Details Navigation
## Shows Copy Link and Next/Previous buttons.

entitydetails-EntityNavigation--string-list = <glyph></glyph>STRINGS
    .title = Go to String List
entitydetails-EntityNavigation--link = <glyph></glyph>COPY LINK
    .title = Copy Link to String
entitydetails-EntityNavigation--next = <glyph></glyph>NEXT
    .title = Go To Next String (Alt + Down)
entitydetails-EntityNavigation--previous = <glyph></glyph>PREVIOUS
    .title = Go To Previous String (Alt + Up)


## Entity Details Helpers
## Shows helper tabs

entitydetails-Helpers--terms = TERMS
entitydetails-Helpers--no-terms = No terms available.

entitydetails-Helpers--comments = COMMENTS
entitydetails-Helpers--no-comments = No comments available.

entitydetails-Helpers--machinery = MACHINERY
entitydetails-Helpers--locales = LOCALES

## Entity Details Metadata
## Shows metadata about an entity (original string)

entitydetails-Metadata--comment =
    .title = COMMENT

entitydetails-Metadata--group-comment =
    .title = GROUP COMMENT

entitydetails-Metadata--resource-comment =
    .title = RESOURCE COMMENT

entitydetails-Metadata--pinned-comment =
    .title = PINNED COMMENT

entitydetails-Metadata--see-more = See More

entitydetails-Metadata--context =
    .title = CONTEXT

entitydetails-Metadata--placeholder =
    .title = PLACEHOLDER EXAMPLES

entitydetails-Metadata--attribute =
    .title = FLUENT ATTRIBUTE

entitydetails-Metadata--entity-created-date =
    .title = CREATED

## Entity Details ContextIssueButton
## Shows the request context or report issue button

entitydetails-ContextIssueButton--context-issue-button = REQUEST CONTEXT or REPORT ISSUE


## Entities List Entity
## Displays a single Entity as a list element

entitieslist-Entity--sibling-strings-title =
    .title = Click to reveal sibling strings

entitieslist-EntitiesList--clear-selected = <glyph></glyph>CLEAR
    .title = Uncheck selected strings

entitieslist-EntitiesList--edit-selected =
    EDIT <stress>{ $count }</stress> { $count ->
        [one] STRING
       *[other] STRINGS
    }<glyph></glyph>
    .title = Edit Selected Strings


## Translation Form

translationform--label-with-example = { $label } (e.g. <stress>{ $example }</stress>)
translationform--single-field-placeholder = Type translation and press Enter to save


## History
## Shows a list of translations for a specific entity

history-History--no-translations = No translations available.


## History Translation
## Shows a specific translation for an entity, and actions around it

history-Translation--copy =
    .title = Copy Into Translation

history-Translation--toggle-diff = DIFF
    .title = Toggle diff against the currently active translation

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

history-Translation--button-comment = COMMENT
    .title = Toggle translation comments

history-Translation--button-comments = { $commentCount ->
        [one] <stress>{ $commentCount }</stress> COMMENT
       *[other] <stress>{ $commentCount }</stress> COMMENTS
    }
    .title = Toggle translation comments

history-Translation--span-copied =
    .title = Copied ({ $machinerySources })

history-translation--approved =
    .title = Approved by { $user } on { DATETIME($reviewedDate, dateStyle:"long", timeStyle:"medium") }
history-translation--approved-anonymous =
    .title = Approved on { DATETIME($reviewedDate, dateStyle:"long", timeStyle:"medium") }
history-translation--rejected =
    .title = Rejected by { $user } on { DATETIME($reviewedDate, dateStyle:"long", timeStyle:"medium") }
history-translation--rejected-anonymous =
    .title = Rejected on { DATETIME($reviewedDate, dateStyle:"long", timeStyle:"medium") }
history-translation--unreviewed =
    .title = Not reviewed yet


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
    On the right hand side, logged-in users can access notifications
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

interactivetour-InteractiveTour--terms-title = Terms
interactivetour-InteractiveTour--terms-content =
    The Terms panel contains specialized words (terms) found in the
    source string, along with their definitions, usage examples, part
    of speech and translations. By clicking on a term, its translation
    gets inserted into the editor.

interactivetour-InteractiveTour--comments-title = Comments
interactivetour-InteractiveTour--comments-content =
    In the Comments tab you can discuss how to translate content with
    your fellow team members. It’s also the place where you can request
    more context about or report an issue in the source string.

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

interactivetour-InteractiveTour--email-communications-title = Let’s keep in touch
interactivetour-InteractiveTour--email-communications-content =
    Want to stay up to date and informed about all localization matters
    at Mozilla? Enable email communications from your <a>settings</a> to get
    the latest updates about localization at Mozilla, announcements about
    new Pontoon features, invitations to contributor events and more.
interactivetour-InteractiveTour--email-communications-footer =
    (Make sure that you’re logged in to access your settings.)

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
    .placeholder = Concordance Search

machinery-Machinery--load-more = LOAD MORE


## Machinery Caighdean Translation
## Shows the translation source from Caighdean Machine Translation.
machinery-CaighdeanTranslation--translation-source = CAIGHDEAN


## Machinery Concordance Search
## Shows concordance search results from Pontoon's memory.
machinery-ConcordanceSearch--translation-memory = TRANSLATION MEMORY


## Machinery Google Translation
## Shows the translation source from Google Translate.
machinery-GoogleTranslation--translation-source = GOOGLE TRANSLATE
machinery-GoogleTranslation--selector =
    .title = Refine using AI
machinery-GoogleTranslation--dropdown-title = AI

machinery-GoogleTranslation--option-rephrase = REPHRASE
machinery-GoogleTranslation--option-rephrased = REPHRASED
machinery-GoogleTranslation--option-make-formal = MAKE FORMAL
machinery-GoogleTranslation--option-formal = FORMAL
machinery-GoogleTranslation--option-make-informal = MAKE INFORMAL
machinery-GoogleTranslation--option-informal = INFORMAL
machinery-GoogleTranslation--option-show-original = SHOW ORIGINAL


## Machinery Microsoft Translation
## Shows the translation source from Microsoft Translation.
machinery-MicrosoftTranslation--translation-source = MICROSOFT TRANSLATOR


## Machinery Systran Translate
## Shows the translation source from Systran Translate.
machinery-SystranTranslate--translation-source = SYSTRAN TRANSLATE


## Machinery Microsoft Terminology
## Shows the translation source from Microsoft Terminology.
machinery-MicrosoftTerminology--translation-source = MICROSOFT


## Machinery Translation
## Shows a specific translation from machinery.
machinery-Translation--copy =
    .title = Copy Into Translation (Ctrl + Shift + Down)


## Machinery Translation Memory
## Shows the translation source from Pontoon's memory.
machinery-TranslationMemory--translation-source = TRANSLATION MEMORY
machinery-TranslationMemory--number-occurrences =
    .title = Number of translation occurrences


## Notification Messages
## Messages shown to users after they perform actions.

notification--translation-approved = Translation approved
notification--translation-unapproved = Translation unapproved
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
notification--ftl-not-supported-rich-editor = Translation not supported in rich editor
notification--entity-not-found = Can’t load specified string
notification--string-link-copied = Link copied to clipboard
notification--comment-added = Comment added


## OtherLocales Translation
## Shows a specific translation from a different locale

otherlocales-Translation--copy =
    .title = Copy Into Translation (Ctrl + Shift + Down)

otherlocales-Translation--header-link =
    .title = Open string in { $locale } ({ $code })


## Message terms
## Used to mark specific terms and characters in translations.

highlight-cli-option =
    .title = Command line option
highlight-email =
    .title = Email
highlight-escape =
    .title = Escape sequence
highlight-newline =
    .title = Newline character
highlight-number =
    .title = Number
highlight-placeholder =
    .title = Placeholder
highlight-placeholder-entity =
    .title = HTML/XML entity
highlight-placeholder-html =
    .title = HTML tag
highlight-placeholder-printf =
    .title = Printf format string
highlight-punctuation =
    .title = Punctuation
highlight-spaces =
    .title = Unusual space
highlight-tab =
    .title = Tab character
highlight-url =
    .title = URL


## Project menu
## Used in the project menu in the main navigation bar.
project-ProjectMenu--no-results = No results
project-ProjectMenu--project = PROJECT
project-ProjectMenu--progress = PROGRESS
project-ProjectMenu--all-projects = All Projects
project-ProjectMenu--search-placeholder =
    .placeholder = Filter projects


## Resource menu
## Used in the resource menu in the main navigation bar.
resource-ResourceMenu--no-results = No results
resource-ResourceMenu--resource = RESOURCE
resource-ResourceMenu--progress = PROGRESS
resource-ResourceMenu--all-resources = All Resources
resource-ResourceMenu--all-projects = All Projects
resource-ResourceMenu--search-placeholder =
    .placeholder = Filter resources


## Filters Panel
## Shows a list of filters, used to filter the list of entities.
search-FiltersPanel--heading-status = TRANSLATION STATUS
search-FiltersPanel--heading-tags = TAGS
search-FiltersPanel--heading-extra = EXTRA FILTERS
search-FiltersPanel--heading-authors = TRANSLATION AUTHORS
search-FiltersPanel--status-name-all = All
search-FiltersPanel--status-name-translated = Translated
search-FiltersPanel--status-name-pretranslated = Pretranslated
search-FiltersPanel--status-name-warnings = Warnings
search-FiltersPanel--status-name-errors = Errors
search-FiltersPanel--status-name-missing = Missing
search-FiltersPanel--status-name-unreviewed = Unreviewed
search-FiltersPanel--extra-name-unchanged = Unchanged
search-FiltersPanel--extra-name-empty = Empty
search-FiltersPanel--extra-name-fuzzy = Fuzzy
search-FiltersPanel--extra-name-rejected = Rejected
search-FiltersPanel--extra-name-missing-without-unreviewed = Missing without Unreviewed

search-FiltersPanel--clear-selection = <glyph></glyph>CLEAR
    .title = Uncheck selected filters

search-FiltersPanel--apply-filters =
    <glyph></glyph>APPLY <stress>{ $count }</stress> { $count ->
        [one] FILTER
       *[other] FILTERS
    }
    .title = Apply Selected Filters


## Search Options Panel

search-SearchPanel--option-name-search-match-case = Match case
search-SearchPanel--option-name-search-match-whole-word = Match whole word
search-SearchPanel--option-name-search-identifiers = Search in string identifiers
search-SearchPanel--option-name-search-rejected-translations = Include rejected translations
search-SearchPanel--option-name-search-exclude-source-strings = Exclude source strings

search-SearchPanel--heading = SEARCH OPTIONS

search-SearchPanel--apply-search-options = APPLY SEARCH OPTIONS
    .title = Apply Selected Search Options

## Time Range Filter
## Time Range filter title, input fields and chart.

search-TimeRangeFilter--heading-time = TRANSLATION TIME
search-TimeRangeFilter--edit-range = <glyph></glyph>EDIT RANGE
search-TimeRangeFilter--save-range = SAVE RANGE


## Term
## Shows term entry with its metadata

term-Term--copy =
    .title = Copy Into Translation

term-Term--for-example = E.G.


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

user-UserMenu--appearance-title = Choose appearance
user-UserMenu--appearance-dark = <glyph></glyph> Dark
    .title = Use a dark theme
user-UserMenu--appearance-light = <glyph></glyph> Light
    .title = Use a light theme
user-UserMenu--appearance-system = <glyph></glyph> System
    .title = Use a theme that matches your system settings

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
user-UserMenu--sync-log = <glyph></glyph>Sync Log

user-UserMenu--settings = <glyph></glyph>Settings


## User Notifications
## Shows user notifications menu.

user-UserNotificationsMenu--no-notifications-title = No new notifications.
user-UserNotificationsMenu--no-notifications-description = Here you’ll see updates for localizations you contribute to.
user-UserNotificationsMenu--see-all-notifications = See all Notifications


## Project Info
## Shows information of all projects

projectinfo-ProjectInfo--project-info-title = PROJECT INFO
