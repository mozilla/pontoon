### Localization for the Translate page of Pontoon


## Pontoon Add-On promotion
## Renders Pontoon Add-On promotion banner

addonpromotion-AddonPromotion--dismiss = ×
    .aria-label = Ttu-t
addonpromotion-AddonPromotion--get = Awi-d azegrir n Pontoon
addonpromotion-AddonPromotion--text = Take your Pontoon notifications everywhere with the official Pontoon Add-on.

## ApproveAll
## Renders Approve All batch action button.

batchactions-ApproveAll--default = SENTEM KULLEC
batchactions-ApproveAll--success =
    { $changedCount ->
        [one] { $changedCount } STRING APPROVED
       *[other] { $changedCount } STRINGS APPROVED
    }
batchactions-ApproveAll--invalid = { $invalidCount } YECCEḌ
batchactions-ApproveAll--error = UHUH! YELLA KRA N WUGUR I D-YEḌRAN

## BatchActions
## Renders batch editor, used for performing mass actions on translations.

batchactions-BatchActions--header-selected-count =
    { $count ->
        [one] <glyph></glyph> <stress>{ $count }</stress> STRING SELECTED
       *[other] <glyph></glyph> <stress>{ $count }</stress> STRINGS SELECTED
    }
    .title = Quit Batch Editing (Esc)
batchactions-BatchActions--header-select-all = <glyph></glyph> FREN-ITEN AKK
    .title = Fren akk izriren (Ctrl + Shift + A)
batchactions-BatchActions--warning = <stress>Warning:</stress> These actions will be applied to all selected strings and cannot be undone.
batchactions-BatchActions--review-heading = SENQED TISUQILIN
batchactions-BatchActions--find-replace-heading = AF-D SAKIN SMELSI DEG TSUQILIN
batchactions-BatchActions--find =
    .placeholder = Af-d
batchactions-BatchActions--replace-with =
    .placeholder = Smelsi s

## RejectAll
## Renders Reject All batch action button.

batchactions-RejectAll--default = AGI AKK ISUMAR
batchactions-RejectAll--confirmation = TETḤEQQEḌ?
batchactions-RejectAll--success =
    { $changedCount ->
        [one] { $changedCount } STRING REJECTED
       *[other] { $changedCount } STRINGS REJECTED
    }
batchactions-RejectAll--invalid = { $invalidCount } YECCEḌ
batchactions-RejectAll--error = UHUH! YELLA KRA N WUGUR I D-YEḌRAN

## ReplaceAll
## Renders Replace All batch action button.

batchactions-ReplaceAll--default = SEMSELSI KULLEC
batchactions-ReplaceAll--success =
    { $changedCount ->
        [one] { $changedCount } STRING REPLACED
       *[other] { $changedCount } STRINGS REPLACED
    }
batchactions-ReplaceAll--invalid = { $invalidCount } YECCEḌ
batchactions-ReplaceAll--error = UHUH! YELLA KRA N WUGUR I D-YEḌRAN

## ResourceProgress
##  Show a panel with progress chart and stats for the current resource.

resourceprogress-ResourceProgress--all-strings = AKK IZRIREN
resourceprogress-ResourceProgress--unreviewed = UR YETTWASENQED ARA
resourceprogress-ResourceProgress--translated = Yettwasuqel
resourceprogress-ResourceProgress--pretranslated = Yettwasuqel s wudem uzwir
resourceprogress-ResourceProgress--warnings = ALƔU
resourceprogress-ResourceProgress--errors = TUCCḌIWIN
resourceprogress-ResourceProgress--missing = IXUṢṢ

## Comments
## Allows user to leave comments on translations and source strings

comments-AddComment--input =
    .placeholder = Aru awennit…
comments-AddComment--mention-avatar-alt =
    .alt = Avaṭar n useqdac
comments-AddComment--submit-button = <glyph></glyph>
    .title = Ceyyeɛ awennit
comments-Comment--pin-button = SENTEḌ
    .title = Senteḍ awennit
comments-Comment--unpin-button = UNPIN
    .title = Unpin comment
comments-Comment--pinned = YETTWASENTEḌ
comments-CommentsList--pinned-comments = IWENNITEN INETḌEN
comments-CommentsList--all-comments = AKK IWENNITEN

## Editor Menu
## Allows contributors to modify or propose a translation

editor-EditorMenu--sign-in-to-translate = <form>Qqen</form> i wakken ad tessuqleḍ.
editor-EditorMenu--read-only-localization = This is a read-only localization.
editor-EditorMenu--button-copy = NƔEL
    .title = Nɣel seg uɣbalu (Ctrl + Shift + C)
editor-EditorMenu--button-clear = SFEḌ
    .title = Sfeḍ tasuqilt (Ctrl + Shift + Backspace)
editor-EditorMenu--button-approve = APPROVE
    .title = Approve Translation (Enter)
editor-EditorMenu--button-approving = <glyph></glyph>APPROVING
    .title = Approving Translation…
editor-EditorMenu--button-save = SEKLES
    .title = Sekles tasuqilt (Kcem)
editor-EditorMenu--button-saving = <glyph></glyph>ASEKLES
    .title = Asekles n tsuqilt…
editor-EditorMenu--button-suggest = SUMER
    .title = Sumer tasuqilt (Kcem)
editor-EditorMenu--button-suggesting = <glyph></glyph>ASUMER
    .title = Asumer n tsuqilt…

## Editor Settings
## Shows options to update user settings regarding the editor.

editor-EditorSettings--toolkit-checks = <glyph></glyph>Translate Toolkit checks
    .title = Run Translate Toolkit checks before submitting translations
editor-EditorSettings--force-suggestions = <glyph></glyph>Make suggestions
    .title = Save suggestions instead of translations
editor-EditorSettings--change-all = Senfel akk iɣewwaren

## Editor FTL Source Editor Switch
## A button that allows switching the editor to/from FTL source mode.

editor-FtlSwitch--toggle =
    .title = Toggle between simple and advanced FTL mode
editor-FtlSwitch--active =
    .title = Askar FTL leqqayen yermed

## Editor Failed Checks
## Renders the failed checks popup

editor-FailedChecks--close = ×
    .aria-label = Close failed checks popup
editor-FailedChecks--title = THE FOLLOWING CHECKS HAVE FAILED
editor-FailedChecks--save-anyway = SEKLES AKKEN IBƔU YILI
editor-FailedChecks--suggest-anyway = SUMER AKKEN IBƔU YILI
editor-FailedChecks--approve-anyway = SENTEM AKKEN IBƔU YILI

## Editor Keyboard Shortcuts
## Shows a list of keyboard shortcuts.

editor-KeyboardShortcuts--button =
    .title = Inegzumen n unasiw
editor-KeyboardShortcuts--overlay-title = INEGZUMEN N UNASIW
editor-KeyboardShortcuts--save-translation = Sekles tasuqilt
editor-KeyboardShortcuts--save-translation-shortcut = <accel>Enter</accel>
editor-KeyboardShortcuts--cancel-translation = Semmet tasuqilt
editor-KeyboardShortcuts--cancel-translation-shortcut = <accel>Esc</accel>
editor-KeyboardShortcuts--insert-a-new-line = Err izirig amaynut
editor-KeyboardShortcuts--insert-a-new-line-shortcut = <mod1>Shift</mod1> + <accel>Enter</accel>
editor-KeyboardShortcuts--go-to-previous-string = Ddu ɣer uzrir yezrin
editor-KeyboardShortcuts--go-to-previous-string-shortcut = <mod1>Alt</mod1> + <accel>Asawen</accel>
editor-KeyboardShortcuts--go-to-next-string = Ddu ɣer uzrir uḍfir
editor-KeyboardShortcuts--go-to-next-string-shortcut = <mod1>Alt</mod1> + <accel>Akessar</accel>
editor-KeyboardShortcuts--copy-from-source = Nɣel seg uɣbalu
editor-KeyboardShortcuts--copy-from-source-shortcut = <mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>C</accel>
editor-KeyboardShortcuts--clear-translation = Sfeḍ tasuqilt
editor-KeyboardShortcuts--clear-translation-shortcut = <mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>Backspace</accel>
editor-KeyboardShortcuts--search-strings = Nadi deg izriren
editor-KeyboardShortcuts--search-strings-shortcut = <mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>F</accel>
editor-KeyboardShortcuts--select-all-strings = Fren akk izriren
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
editor-BadgeTooltip--level = Aswir { $badgeLevel }
editor-BadgeTooltip--profile = View your new badge in your <a>profile</a>.
editor-BadgeTooltip--continue = Kemmel

## Editor Unsaved Changes
## Renders the unsaved changes popup

editor-UnsavedChanges--close = ×
    .aria-label = Close unsaved changes popup
editor-UnsavedChanges--title = TESƐIḌ ISENFAL UR YETTWAKLASEN ARA
editor-UnsavedChanges--body = Tetḥeqqeḍ tebɣiḍ ad tkemmleḍ?
editor-UnsavedChanges--proceed = KEMMEL

## Entity Details Navigation
## Shows Copy Link and Next/Previous buttons.

entitydetails-EntityNavigation--string-list = <glyph></glyph>STRINGS
    .title = Go to String List
entitydetails-EntityNavigation--link = <glyph></glyph>NƔEL ASEƔWEN
    .title = Nɣel aseɣwen ar uzrir
entitydetails-EntityNavigation--next = <glyph></glyph>NEXT
    .title = Go To Next String (Alt + Down)
entitydetails-EntityNavigation--previous = <glyph></glyph>PREVIOUS
    .title = Go To Previous String (Alt + Up)

## Entity Details Helpers
## Shows helper tabs

entitydetails-Helpers--terms = TIWTILIN
entitydetails-Helpers--no-terms = Ulac tiwtilin.
entitydetails-Helpers--comments = IWENNITEN
entitydetails-Helpers--no-comments = Ulac iwenniten.
entitydetails-Helpers--machinery = MACHINERY
entitydetails-Helpers--locales = TUTLAYIN

## Entity Details Metadata
## Shows metadata about an entity (original string)

entitydetails-Metadata--comment =
    .title = Awennit
entitydetails-Metadata--group-comment =
    .title = GROUP COMMENT
entitydetails-Metadata--resource-comment =
    .title = RESOURCE COMMENT
entitydetails-Metadata--pinned-comment =
    .title = PINNED COMMENT
entitydetails-Metadata--see-more = Wali ugar
entitydetails-Metadata--context =
    .title = ASATAL
entitydetails-Metadata--placeholder =
    .title = PLACEHOLDER EXAMPLES
entitydetails-Metadata--attribute =
    .title = FLUENT ATTRIBUTE
entitydetails-Metadata--entity-created-date =
    .title = YETTWARNA

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
    ẒREG <stress>{ $count }</stress> { $count ->
        [one] N UZRIR
       *[other] N YEZRIREN
    }<glyph></glyph>
    .title = Ẓreg izriren yettwafernen

## Translation Form

translationform--label-with-example = { $label } (amedya <stress>{ $example }</stress>)
translationform--single-field-placeholder = Aru tasuqilt sakin sit ɣef "Ukeččum" akken ad t-teskelseḍ

## History
## Shows a list of translations for a specific entity

history-History--no-translations = Ulac tisuqilin yellan.

## History Translation
## Shows a specific translation for an entity, and actions around it

history-Translation--copy =
    .title = Nɣel-it ar tsuqilt
history-Translation--toggle-diff = DIFF
    .title = Toggle diff against the currently active translation
history-Translation--button-delete =
    .title = Kkes
history-Translation--button-approve =
    .title = Sentem
history-Translation--button-unapprove =
    .title = UR yettwasentem ara
history-Translation--button-reject =
    .title = Agi
history-Translation--button-unreject =
    .title = Ur yettwagi ara
history-Translation--button-not-approved =
    .title = Not approved
history-Translation--button-approved =
    .title = Yettwaqbel
history-Translation--button-not-rejected =
    .title = Not rejected
history-Translation--button-rejected =
    .title = Yettwagi
history-Translation--button-comment = COMMENT
    .title = Toggle translation comments
history-Translation--button-comments =
    { $commentCount ->
        [one] <stress>{ $commentCount }</stress> N UWENNIT
       *[other] <stress>{ $commentCount }</stress> N IWENNITEN
    }
    .title = Toggle translation comments
history-Translation--span-copied =
    .title = Yenɣel ({ $machinerySources })
history-translation--approved =
    .title = Approved by { $user } on { DATETIME($reviewedDate, dateStyle: "long", timeStyle: "medium") }
history-translation--approved-anonymous =
    .title = Approved on { DATETIME($reviewedDate, dateStyle: "long", timeStyle: "medium") }
history-translation--rejected =
    .title = Rejected by { $user } on { DATETIME($reviewedDate, dateStyle: "long", timeStyle: "medium") }
history-translation--rejected-anonymous =
    .title = Rejected on { DATETIME($reviewedDate, dateStyle: "long", timeStyle: "medium") }
history-translation--unreviewed =
    .title = Not reviewed yet

## Interactive Tour
## Shows an interactive Tour on the "Tutorial" project,
## introducing the translate page of Pontoon.

interactivetour-InteractiveTour--intro-title = Azul dinna !
interactivetour-InteractiveTour--intro-content =
    Pontoon d annar n usideg sɣur Mozilla, i yettwaseqdacen i usideg
    n Firefox akked yisenfaren-nniḍen yemgaraden di Mozilla akked tuddsiwin-nniḍen.
interactivetour-InteractiveTour--intro-footer = Ḍfer amnir-a akken ad tlemdeḍ amek ara t-tesqedceḍ.
interactivetour-InteractiveTour--main-toolbar-title = Afeggag n ifecka agejdan
interactivetour-InteractiveTour--main-toolbar-content =
    The main toolbar located on top of the screen shows the language,
    project and resource currently being localized. You can also
    see the progress of your current localization and additional
    project information.
interactivetour-InteractiveTour--main-toolbar-footer =
    On the right hand side, logged-in users can access notifications
    and settings.
interactivetour-InteractiveTour--string-list-title = Tabdart n yizriren
interactivetour-InteractiveTour--string-list-content =
    The sidebar displays a list of strings in the current
    localization. Status of each string (e.g. Translated or Missing)
    is indicated by a different color of the square on the left. The
    square also acts as a checkbox for selecting strings to perform
    mass actions on.
interactivetour-InteractiveTour--string-list-footer =
    On top of the list is a search box, which allows you to
    search source strings, translations, comments and string IDs.
interactivetour-InteractiveTour--filters-title = Imsizdigen
interactivetour-InteractiveTour--filters-content =
    Strings can also be filtered by their status, translation time,
    translation authors and other criteria. Note that filter icons act
    as checkboxes, which allows you to filter by multiple criteria.
interactivetour-InteractiveTour--editor-title = Amaẓrag
interactivetour-InteractiveTour--editor-content =
    Clicking a string in the list opens it in the editor. On top of
    it, you can see the source string with its context. Right under
    that is the translation input to type translation in, followed
    by the translation toolbar.
interactivetour-InteractiveTour--submit-title = Ceyyeɛ tasuqilt
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
interactivetour-InteractiveTour--history-title = Amazray
interactivetour-InteractiveTour--history-content =
    All suggestions and translations submitted for the current
    string can be found in the History Tab. Icons to the right of
    each entry indicate its review status (Approved, Rejected or
    Unreviewed).
interactivetour-InteractiveTour--terms-title = Tiwtilin
interactivetour-InteractiveTour--terms-content =
    The Terms panel contains specialized words (terms) found in the
    source string, along with their definitions, usage examples, part
    of speech and translations. By clicking on a term, its translation
    gets inserted into the editor.
interactivetour-InteractiveTour--comments-title = Iwenniten
interactivetour-InteractiveTour--comments-content =
    In the Comments tab you can discuss how to translate content with
    your fellow team members. It’s also the place where you can request
    more context about or report an issue in the source string.
interactivetour-InteractiveTour--machinery-title = Machinery
interactivetour-InteractiveTour--machinery-content =
    The Machinery tab shows automated translation suggestions from
    Machine Translation, Translation Memory and Terminology services.
    Clicking on an entry copies it to the translation input.
interactivetour-InteractiveTour--locales-title = Tutlayin
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
interactivetour-InteractiveTour--email-communications-footer = (Make sure that you’re logged in to access your settings.)
interactivetour-InteractiveTour--end-title = (Mačči) d aya kan a timeddukal!
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
machinery-Machinery--load-more = SALI-D UGAR

## Machinery Caighdean Translation
## Shows the translation source from Caighdean Machine Translation.

machinery-CaighdeanTranslation--translation-source = CAIGHDEAN

## Machinery Concordance Search
## Shows concordance search results from Pontoon's memory.

machinery-ConcordanceSearch--translation-memory = TAKATUT N TSUQILT

## Machinery Google Translation
## Shows the translation source from Google Translate.

machinery-GoogleTranslation--translation-source = GOOGLE TRANSLATE
machinery-GoogleTranslation--selector =
    .title = Refine using AI
machinery-GoogleTranslation--dropdown-title = AI
machinery-GoogleTranslation--option-rephrase = REPHRASE
machinery-GoogleTranslation--option-rephrased = REPHRASED
machinery-GoogleTranslation--option-make-formal = ERR D ALƔAWAN
machinery-GoogleTranslation--option-formal = ALƔAW
machinery-GoogleTranslation--option-make-informal = ERR-IT D ARALƔAWAN
machinery-GoogleTranslation--option-informal = ARALƔAWAN
machinery-GoogleTranslation--option-show-original = SKEN AƔBALU

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
    .title = Nɣel-it ar tsuqilt (Ctrl + Shift + Down)

## Machinery Translation Memory
## Shows the translation source from Pontoon's memory.

machinery-TranslationMemory--translation-source = TAKATUT N TSUQILT
machinery-TranslationMemory--number-occurrences =
    .title = Number of translation occurrences

## Notification Messages
## Messages shown to users after they perform actions.

notification--translation-approved = Tasuqqilt tettwaqbel
notification--translation-unapproved = Ur tettwasenten ara tsuqilt
notification--translation-rejected = Tettwagi tsuqilt
notification--translation-unrejected = Translation unrejected
notification--translation-deleted = Tettwakes tsuqilt
notification--translation-saved = Tettwaskles tsuqilt
notification--unable-to-approve-translation = Unable to approve translation
notification--unable-to-unapprove-translation = Unable to unapprove translation
notification--unable-to-reject-translation = Unable to reject translation
notification--unable-to-unreject-translation = Unable to unreject translation
notification--unable-to-delete-translation = Unable to delete translation
notification--same-translation = Tella yakan yiwet n tsuqilt am ta
notification--tt-checks-enabled = Translate Toolkit Checks enabled
notification--tt-checks-disabled = Translate Toolkit Checks disabled
notification--make-suggestions-enabled = Err isumar urmiden
notification--make-suggestions-disabled = Err isumar arurmiden
notification--ftl-not-supported-rich-editor = Translation not supported in rich editor
notification--entity-not-found = Can’t load specified string
notification--string-link-copied = Aseɣwen yettwanɣel ɣef wafus
notification--comment-added = Yettwarna uwennit

## OtherLocales Translation
## Shows a specific translation from a different locale

otherlocales-Translation--copy =
    .title = Nɣel-it ar tasuqilt (Ctrl + Shift + Down)
otherlocales-Translation--header-link =
    .title = Ldi azrir s { $locale } ({ $code })

## Message terms
## Used to mark specific terms and characters in translations.

highlight-cli-option =
    .title = Command line option
highlight-email =
    .title = Imayl
highlight-escape =
    .title = Escape sequence
highlight-newline =
    .title = Asekkil n yizirig amaynut
highlight-number =
    .title = Uṭṭun
highlight-placeholder =
    .title = Placeholder
highlight-placeholder-entity =
    .title = HTML/XML entity
highlight-placeholder-html =
    .title = Tabzimt HTML
highlight-placeholder-printf =
    .title = Printf format string
highlight-punctuation =
    .title = Asigez
highlight-spaces =
    .title = Unusual space
highlight-tab =
    .title = Tab character
highlight-url =
    .title = URL

## Project menu
## Used in the project menu in the main navigation bar.

project-ProjectMenu--no-results = Ulac igmaḍ
project-ProjectMenu--project = ASENFAR
project-ProjectMenu--progress = ITEDDU
project-ProjectMenu--all-projects = Akk isenfaren
project-ProjectMenu--search-placeholder =
    .placeholder = Sizdeg isenfaren

## Resource menu
## Used in the resource menu in the main navigation bar.

resource-ResourceMenu--no-results = Ulac igmaḍ
resource-ResourceMenu--resource = AƔBALU
resource-ResourceMenu--progress = ITEDDU
resource-ResourceMenu--all-resources = Akk tiɣbula
resource-ResourceMenu--all-projects = Akk isenfaren
resource-ResourceMenu--search-placeholder =
    .placeholder = Filter resources

## Filters Panel
## Shows a list of filters, used to filter the list of entities.

search-FiltersPanel--heading-status = ADDAD N TSUQILT
search-FiltersPanel--heading-tags = TIBZIMIN
search-FiltersPanel--heading-extra = IMSIZDIGEN NNIḌEN
search-FiltersPanel--heading-authors = IMESKAREN N TSUQILT
search-FiltersPanel--status-name-all = Akk
search-FiltersPanel--status-name-translated = Yettwasuqqlen
search-FiltersPanel--status-name-pretranslated = Pretranslated
search-FiltersPanel--status-name-warnings = Alɣu
search-FiltersPanel--status-name-errors = Tuccḍiwin
search-FiltersPanel--status-name-missing = Ixuṣṣ
search-FiltersPanel--status-name-unreviewed = Ur yettwasenqed ara
search-FiltersPanel--extra-name-unchanged = Ur yettwasenfal ara
search-FiltersPanel--extra-name-empty = D tilemt
search-FiltersPanel--extra-name-fuzzy = Fuzzy
search-FiltersPanel--extra-name-rejected = Yettwagi
search-FiltersPanel--extra-name-missing-without-unreviewed = Missing without Unreviewed
search-FiltersPanel--clear-selection = <glyph></glyph>SFEḌ
    .title = Uncheck selected filters
search-FiltersPanel--apply-filters =
    <glyph></glyph>SNES <stress>{ $count }</stress> { $count ->
        [one] N UMSIZDEG
       *[other] N YIMSIZDIGEN
    }
    .title = Snes imsizdigen yettwafernen

## Search Options Panel

search-SearchPanel--option-name-search-match-case = Match case
search-SearchPanel--option-name-search-match-whole-word = Amṣada n wawal ummid
search-SearchPanel--option-name-search-identifiers = Search in string identifiers
search-SearchPanel--option-name-search-rejected-translations = Seddu tisuqqilin yettwagin
search-SearchPanel--option-name-search-exclude-source-strings = Kkes izriren iɣbula
search-SearchPanel--heading = TIXTIṚIYIN N UNADI
search-SearchPanel--apply-search-options = SNES TIXTIṚIYIN N UNAFI
    .title = Apply Selected Search Options

## Time Range Filter
## Time Range filter title, input fields and chart.

search-TimeRangeFilter--heading-time = AKUD N USUQQEL
search-TimeRangeFilter--edit-range = <glyph></glyph>EDIT RANGE
search-TimeRangeFilter--save-range = SEKLES AZILAL

## Term
## Shows term entry with its metadata

term-Term--copy =
    .title = Nɣel-it ar tsuqilt
term-Term--for-example = MD.

## User Avatar
## Shows user Avatar with alt text

user-UserAvatar--anon-alt-text =
    .alt = Aseqdac arussin
user-UserAvatar--alt-text =
    .alt = Amaɣnu n useqdac

## User Menu
## Shows user menu entries and options to sign in or out.

user-SignIn--sign-in = QQEN
user-SignOut--sign-out = <glyph></glyph>Ffeɣ
user-UserMenu--appearance-title = Fren arwes
user-UserMenu--appearance-dark = <glyph></glyph> Dark
    .title = Use a dark theme
user-UserMenu--appearance-light = <glyph></glyph> Light
    .title = Use a light theme
user-UserMenu--appearance-system = <glyph></glyph> Anagraw
    .title = Seqdec asentel yeddan d yiɣewwaren n unagraw-ik·im
user-UserMenu--download-terminology = <glyph></glyph>SAder Amawal
user-UserMenu--download-tm = <glyph></glyph>Zdem-d takatut n tsuqilt
user-UserMenu--download-translations = <glyph></glyph>Zdem-d tisuqilin
user-UserMenu--upload-translations = <glyph></glyph>Sali tisuqilin
user-UserMenu--terms = <glyph></glyph>Tiwtilin n useqdec
user-UserMenu--github = <glyph></glyph>Hack it on GitHub
user-UserMenu--feedback = <glyph></glyph>Mudd tamawt
user-UserMenu--help = <glyph></glyph>Tallalt
user-UserMenu--admin = <glyph></glyph>Anedbal
user-UserMenu--admin-project = <glyph></glyph>Admin · Current Project
user-UserMenu--sync-log = <glyph></glyph>Aɣmis n umtawi
user-UserMenu--settings = <glyph></glyph>Iɣewwaren

## User Notifications
## Shows user notifications menu.

user-UserNotificationsMenu--no-notifications-title = Ulac ilɣa imaynuten.
user-UserNotificationsMenu--no-notifications-description = Here you’ll see updates for localizations you contribute to.
user-UserNotificationsMenu--see-all-notifications = Wali akk ilɣa

## Project Info
## Shows information of all projects

projectinfo-ProjectInfo--project-info-title = TALƔUT N USENFAR
