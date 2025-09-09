### Localization for the Translate page of Pontoon
### Swedísh translation by Daniel Nylander <po@danielnylander.se>

## Pontoon Add-On promotion
## Renders Pontoon Add-On promotion banner

addonpromotion-AddonPromotion--dismiss = ×
    .aria-label = Stäng
addonpromotion-AddonPromotion--get = Skaffa Pontoon-tillägget
addonpromotion-AddonPromotion--text = Ta med dina Pontoon-aviseringar överallt med det officiella Pontoon-tillägget.


## ApproveAll
## Renders Approve All batch action button.

batchactions-ApproveAll--default = GODKÄNN ALLA
batchactions-ApproveAll--success =
    { $changedCount ->
        [one] { $changedCount } STRÄNG GODKÄND
       *[other] { $changedCount } STRÄNGAR GODKÄNDA
    }
batchactions-ApproveAll--invalid = { $invalidCount } MISSLYCKADES
batchactions-ApproveAll--error = HOPPSAN, NÅGOT GICK FEL


## BatchActions
## Renders batch editor, used for performing mass actions on translations.

batchactions-BatchActions--header-selected-count =
    { $count ->
        [one] <glyph></glyph> <stress>{ $count }</stress> STRÄNG MARKERAD
       *[other] <glyph></glyph> <stress>{ $count }</stress> STRÄNGAR MARKERADE
    }
    .title = Avsluta massredigering (Esc)
batchactions-BatchActions--header-select-all = <glyph></glyph> MARKERA ALLA
    .title = Markera alla strängar (Ctrl + Shift + A)

batchactions-BatchActions--warning = <stress>Varning:</stress> Dessa åtgärder kommer att tillämpas på alla valda strängar och kan inte ångras.

batchactions-BatchActions--review-heading = GRANSKA ÖVERSÄTTNINGAR

batchactions-BatchActions--find-replace-heading = SÖK OCH ERSÄTT I ÖVERSÄTTNINGAR
batchactions-BatchActions--find =
    .placeholder = Sök
batchactions-BatchActions--replace-with =
    .placeholder = Ersätt med


## RejectAll
## Renders Reject All batch action button.

batchactions-RejectAll--default = AVVISA ALLA FÖRSLAG
batchactions-RejectAll--confirmation = ÄR DU SÄKER?
batchactions-RejectAll--success =
    { $changedCount ->
        [one] { $changedCount } STRÄNG AVVISADES
       *[other] { $changedCount } STRÄNGAR AVVISADES
    }
batchactions-RejectAll--invalid = { $invalidCount } MISSLYCKADES
batchactions-RejectAll--error = HOPPSAN, NÅGOT GICK FEL


## ReplaceAll
## Renders Replace All batch action button.

batchactions-ReplaceAll--default = ERSÄTT ALLA
batchactions-ReplaceAll--success =
    { $changedCount ->
        [one] { $changedCount } STRÄNG ERSATT
       *[other] { $changedCount } STRÄNGAR ERSÄTTA
    }
batchactions-ReplaceAll--invalid = { $invalidCount } MISSLYCKADES
batchactions-ReplaceAll--error = HOPPSAN, NÅGOT GICK FEL


## ResourceProgress
##  Show a panel with progress chart and stats for the current resource.

resourceprogress-ResourceProgress--all-strings = ALLA STRÄNGAR
resourceprogress-ResourceProgress--unreviewed = OGRANSKADE
resourceprogress-ResourceProgress--translated = ÖVERSATTA
resourceprogress-ResourceProgress--pretranslated = FÖRHANDSÖVERSATTA
resourceprogress-ResourceProgress--warnings = VARNINGAR
resourceprogress-ResourceProgress--errors = FEL
resourceprogress-ResourceProgress--missing = SAKNAS


## Comments
## Allows user to leave comments on translations and source strings

comments-AddComment--input =
    .placeholder = Skriv en kommentar…
comments-AddComment--mention-avatar-alt =
    .alt = Användaravatar
comments-AddComment--submit-button = <glyph></glyph>
    .title = Skicka in kommentar
comments-Comment--pin-button = NÅLA
    .title = Nåla kommentar
comments-Comment--unpin-button = AVNÅLA
    .title = Avnåla kommentar
comments-Comment--pinned = NÅLAD
comments-CommentsList--pinned-comments = NÅLADE KOMMENTARER
comments-CommentsList--all-comments = ALLA KOMMENTARER


## Editor Menu
## Allows contributors to modify or propose a translation

editor-EditorMenu--sign-in-to-translate = <form>Logga in</form> för att översätta.
editor-EditorMenu--read-only-localization = Detta är en skrivskyddad lokalisering..
editor-EditorMenu--button-copy = KOPIERA
    .title = Kopiera från källa (Ctrl + Shift + C)
editor-EditorMenu--button-clear = TÖM
    .title = Töm översättning (Ctrl + Shift + Backspace)
editor-EditorMenu--button-approve = GODKÄNN
    .title = Godkänn översättning (Enter)
editor-EditorMenu--button-approving = <glyph></glyph>GODKÄNNER
    .title = Godkänner översättning…
editor-EditorMenu--button-save = SPARA
    .title = Spara översättning (Enter)
editor-EditorMenu--button-saving = <glyph></glyph>SPARAR
    .title = Sparar översättning…
editor-EditorMenu--button-suggest = FÖRESLÅ
    .title = Föreslå översättning (Enter)
editor-EditorMenu--button-suggesting = <glyph></glyph>FÖRESLÅR
    .title = Föreslår översättning…


## Editor Settings
## Shows options to update user settings regarding the editor.

editor-EditorSettings--toolkit-checks = <glyph></glyph>Translate Toolkit-kontroller
    .title = Kör Translate Toolkit-kontroller innan du skickar in översättningar

editor-EditorSettings--force-suggestions = <glyph></glyph>Gör förslag
    .title = Spara förslag istället för översättningar

editor-EditorSettings--change-all = Ändra alla inställningar


## Editor FTL Source Editor Switch
## A button that allows switching the editor to/from FTL source mode.

editor-FtlSwitch--toggle =
    .title = Växla mellan enkelt och avancerat FTL-läge

editor-FtlSwitch--active =
    .title = Avancerat FTL-läge aktiverat


## Editor Failed Checks
## Renders the failed checks popup

editor-FailedChecks--close = ×
    .aria-label = Stäng popup-fönster för misslyckade kontroller
editor-FailedChecks--title = FÖLJANDE KONTROLLER HAR MISSLYCKATS
editor-FailedChecks--save-anyway = SPARA ÄNDÅ
editor-FailedChecks--suggest-anyway = FÖRESLÅ ÄNDÅ
editor-FailedChecks--approve-anyway = GODKÄNN ÄNDÅ


## Editor Keyboard Shortcuts
## Shows a list of keyboard shortcuts.

editor-KeyboardShortcuts--button =
    .title = Keyboard Shortcuts

editor-KeyboardShortcuts--overlay-title = TANGENTBORDSGENVÄGAR

editor-KeyboardShortcuts--save-translation = Spara översättning
editor-KeyboardShortcuts--save-translation-shortcut = <accel>Enter</accel>

editor-KeyboardShortcuts--cancel-translation = Avbryt översättning
editor-KeyboardShortcuts--cancel-translation-shortcut = <accel>Esc</accel>

editor-KeyboardShortcuts--insert-a-new-line = Infoga en ny rad
editor-KeyboardShortcuts--insert-a-new-line-shortcut = <mod1>Shift</mod1> + <accel>Enter</accel>

editor-KeyboardShortcuts--go-to-previous-string = Gå till föregående sträng
editor-KeyboardShortcuts--go-to-previous-string-shortcut = <mod1>Alt</mod1> + <accel>Up</accel>

editor-KeyboardShortcuts--go-to-next-string = Gå till nästa sträng
editor-KeyboardShortcuts--go-to-next-string-shortcut = <mod1>Alt</mod1> + <accel>Down</accel>

editor-KeyboardShortcuts--copy-from-source = Kopiera från källa
editor-KeyboardShortcuts--copy-from-source-shortcut = <mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>C</accel>

editor-KeyboardShortcuts--clear-translation = Töm översättning
editor-KeyboardShortcuts--clear-translation-shortcut = <mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>Backspace</accel>

editor-KeyboardShortcuts--search-strings = Sök efter strängar
editor-KeyboardShortcuts--search-strings-shortcut = <mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>F</accel>

editor-KeyboardShortcuts--select-all-strings = Markera alla strängar
editor-KeyboardShortcuts--select-all-strings-shortcut = <mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>A</accel>

editor-KeyboardShortcuts--copy-from-previous-helper = Kopiera från föregående hjälpare
editor-KeyboardShortcuts--copy-from-previous-helper-shortcut = <mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>Up</accel>

editor-KeyboardShortcuts--copy-from-next-helper = Kopiera från nästa hjälpare
editor-KeyboardShortcuts--copy-from-next-helper-shortcut = <mod1>Ctrl</mod1> + <mod2>Shift</mod2> + <accel>Down</accel>


## Editor machinery source indicator
## Shown when a perfect match is provided automatically from translation memory

editor-MachinerySourceIndicator--text = <stress>100%</stress> MATCH FRÅN ÖVERSÄTTNINGSMINNE


## Editor New Contributor Tooltip
## Renders the guidelines for new contributors

editor-NewContributorTooltip--intro = Det verkar som om du ännu inte har bidragit till denna lokalisering.
editor-NewContributorTooltip--team-info = Kontrollera <a>teaminformationen</a> innan du börjar, eftersom den kan innehålla viktig information och språkliga resurser.
editor-NewContributorTooltip--team-managers = Kontakta <a>teamledarna</a> om du har frågor eller vill veta mer om hur du kan bidra.


## Editor Badge Tooltip
## Popup notification when users gain a new badge level

editor-BadgeTooltip--intro = Prestation upplåst
editor-BadgeTooltip--level = Nivå { $badgeLevel }
editor-BadgeTooltip--profile = Se ditt nya märke i din <a>profil</a>.
editor-BadgeTooltip--continue = Fortsätt


## Editor Unsaved Changes
## Renders the unsaved changes popup

editor-UnsavedChanges--close = ×
    .aria-label = Stäng popup-fönstret för osparade ändringar
editor-UnsavedChanges--title = DU HAR OSPARADE ÄNDRINGAR
editor-UnsavedChanges--body = Är du säker på att du vill fortsätta?
editor-UnsavedChanges--proceed = FORTSÄTT


## Entity Details Navigation
## Shows Copy Link and Next/Previous buttons.

entitydetails-EntityNavigation--string-list = <glyph></glyph>STRÄNGAR
    .title = Gå till stränglista
entitydetails-EntityNavigation--link = <glyph></glyph>KOPIERA LÄNK
    .title = Kopiera länk till sträng
entitydetails-EntityNavigation--next = <glyph></glyph>NÄSTA
    .title = Gå till nästa sträng (Alt + Down)
entitydetails-EntityNavigation--previous = <glyph></glyph>FÖREGÅENDE
    .title = Gå till föregående sträng (Alt + Up)


## Entity Details Helpers
## Shows helper tabs

entitydetails-Helpers--terms = TERMER
entitydetails-Helpers--no-terms = Inga termer tillgängliga.

entitydetails-Helpers--comments = KOMMENTARER
entitydetails-Helpers--no-comments = Inga kommentarer tillgängliga.

entitydetails-Helpers--machinery = MASKIN
entitydetails-Helpers--locales = LOKALISERINGAR

## Entity Details Metadata
## Shows metadata about an entity (original string)

entitydetails-Metadata--comment =
    .title = KOMMENTAR

entitydetails-Metadata--group-comment =
    .title = GRUPPKOMMENTAR

entitydetails-Metadata--resource-comment =
    .title = RESURSKOMMENTAR

entitydetails-Metadata--pinned-comment =
    .title = NÅLAD KOMMENTAR

entitydetails-Metadata--see-more = Se mer

entitydetails-Metadata--context =
    .title = KONTEXT

entitydetails-Metadata--placeholder =
    .title = PLATSHÅLLAREXEMPEL

entitydetails-Metadata--attribute =
    .title = FLYTANDE EGENSKAP

entitydetails-Metadata--entity-created-date =
    .title = SKAPAD

## Entity Details ContextIssueButton
## Shows the request context or report issue button

entitydetails-ContextIssueButton--context-issue-button = BEGÄR KONTEXT eller RAPPORTERA PROBLEM


## Entities List Entity
## Displays a single Entity as a list element

entitieslist-Entity--sibling-strings-title =
    .title = Klicka för att visa syskonsträngar

entitieslist-EntitiesList--clear-selected = <glyph></glyph>CLEAR
    .title = Avmarkera valda strängar

entitieslist-EntitiesList--edit-selected =
    REDIGERA <stress>{ $count }</stress> { $count ->
        [one] STRÄNG
       *[other] STRÄNGAR
    }<glyph></glyph>
    .title = Redigera valda strängar


## Translation Form

translationform--label-with-example = { $label } (e.g. <stress>{ $example }</stress>)
translationform--single-field-placeholder = Skriv översättningen och tryck på Enter för att spara


## History
## Shows a list of translations for a specific entity

history-History--no-translations = Inga översättningar tillgängliga.


## History Translation
## Shows a specific translation for an entity, and actions around it

history-Translation--copy =
    .title = Kopiera till översättning

history-Translation--toggle-diff = DIFF
    .title = Växla mellan skillnad mot den aktuellt aktiva översättningen

history-Translation--button-delete =
    .title = Ta bort

history-Translation--button-approve =
    .title = Godkänn

history-Translation--button-unapprove =
    .title = Godkänn inte

history-Translation--button-reject =
    .title = Avvisa

history-Translation--button-unreject =
    .title = Avvisa inte

history-Translation--button-not-approved =
    .title = Godkänn inte

history-Translation--button-approved =
    .title = Godkänd

history-Translation--button-not-rejected =
    .title = Inte avvisad

history-Translation--button-rejected =
    .title = Avvisad

history-Translation--button-comment = COMMENT
    .title = Växla mellan översättningskommentarer

history-Translation--button-comments = { $commentCount ->
        [one] <stress>{ $commentCount }</stress> KOMMENTAR
       *[other] <stress>{ $commentCount }</stress> KOMMENTARER
    }
    .title = Växla mellan översättningskommentarer

history-Translation--span-copied =
    .title = Kopierade ({ $machinerySources })

history-translation--approved =
    .title = Godkänd av { $user } den { DATETIME($reviewedDate, dateStyle:"long", timeStyle:"medium") }
history-translation--approved-anonymous =
    .title = Godkänd den { DATETIME($reviewedDate, dateStyle:"long", timeStyle:"medium") }
history-translation--rejected =
    .title = Avvisad av { $user } den { DATETIME($reviewedDate, dateStyle:"long", timeStyle:"medium") }
history-translation--rejected-anonymous =
    .title = Avvisades den { DATETIME($reviewedDate, dateStyle:"long", timeStyle:"medium") }
history-translation--unreviewed =
    .title = Inte granskad ännu


## Interactive Tour
## Shows an interactive Tour on the "Tutorial" project,
## introducing the translate page of Pontoon.

interactivetour-InteractiveTour--intro-title = Hallå där!
interactivetour-InteractiveTour--intro-content =
    Pontoon är en lokaliseringsplattform från Mozilla som används för att lokalisera
    Firefox och olika andra projekt hos Mozilla och andra organisationer.
interactivetour-InteractiveTour--intro-footer = Följ denna guide för att lära dig hur du använder den.

interactivetour-InteractiveTour--main-toolbar-title = Huvudverktygsfält
interactivetour-InteractiveTour--main-toolbar-content =
    Huvudverktygsfältet längst upp på skärmen visar vilket språk,
    projekt och vilken resurs som lokaliseras för tillfället. Du kan också
    se hur långt du har kommit i din aktuella lokalisering och ytterligare
    projektinformation.
interactivetour-InteractiveTour--main-toolbar-footer =
    På höger sida kan inloggade användare komma åt meddelanden
    och inställningar.

interactivetour-InteractiveTour--string-list-title = Stränglista
interactivetour-InteractiveTour--string-list-content =
    Sidfältet visar en lista över strängar i den aktuella
    lokaliseringen. Status för varje sträng (t.ex. Översatt eller Saknas)
    indikeras av en annan färg på rutan till vänster.
    Rutan fungerar också som en kryssruta för att välja strängar för att utföra
    massåtgärder på.
interactivetour-InteractiveTour--string-list-footer =
    Högst upp på listan finns ett sökruta som gör det möjligt att
    söka efter källsträngar, översättningar, kommentarer och sträng-id:n.

interactivetour-InteractiveTour--filters-title = Filter
interactivetour-InteractiveTour--filters-content =
    Strängar kan också filtreras efter status, översättningstid,
    översättare och andra kriterier. Observera att filterikonerna fungerar
    som kryssrutor, vilket gör att du kan filtrera efter flera kriterier.

interactivetour-InteractiveTour--editor-title = Redigerare
interactivetour-InteractiveTour--editor-content =
    Om du klickar på en sträng i listan öppnas den i redigeraren. Ovanför
    den kan du se källsträngen med dess sammanhang. Direkt under
    finns översättningsfältet där du kan skriva in översättningen, följt
    av översättningsverktygsfältet.

interactivetour-InteractiveTour--submit-title = Skicka in en översättning
interactivetour-InteractiveTour--submit-content-unauthenticated =
    En användare måste vara inloggad för att kunna skicka in översättningar.
    Icke-autentiserade användare ser en länk till Logga in istället för
    översättningsverktygsfältet med en knapp för att spara översättningar.
interactivetour-InteractiveTour--submit-content-contributor =
    När en översättare är i förslagsläge eller inte har behörighet
    att skicka in översättningar direkt visas en blå FÖRESLÅ-knapp
    i översättningsverktygsfältet. För att göra ett förslag skriver du in det i
    översättningsfältet och klickar på FÖRESLÅ.
interactivetour-InteractiveTour--submit-content-translator =
    Om en översättare har behörighet att lägga till översättningar direkt
    visas den gröna knappen SPARA i översättningsverktygsfältet.
    För att skicka en översättning skriver du in den i översättningsfältet och
    klickar på SPARA.

interactivetour-InteractiveTour--history-title = Historik
interactivetour-InteractiveTour--history-content =
    Alla förslag och översättningar som skickats in för den aktuella
    strängen finns under fliken Historik. Ikonerna till höger om
    varje post visar dess granskningsstatus (Godkänd, Avvisad eller
    Ogranskad).

interactivetour-InteractiveTour--terms-title = Termer
interactivetour-InteractiveTour--terms-content =
    Panelen Termer innehåller specialiserade ord (termer) som finns i
    källsträngen, tillsammans med deras definitioner, användningsexempel,
    ordklass och översättningar. Genom att klicka på en term infogas dess
    översättning i redigeraren.

interactivetour-InteractiveTour--comments-title = Kommentarer
interactivetour-InteractiveTour--comments-content =
    På fliken Kommentarer kan du diskutera hur innehållet ska översättas med
    dina kollegor. Här kan du också begära
    mer kontext om eller rapportera ett problem i källtexten.

interactivetour-InteractiveTour--machinery-title = Maskin
interactivetour-InteractiveTour--machinery-content =
    Fliken Maskin visar automatiska översättningsförslag från
    maskinöversättning, översättningsminne och terminologitjänster.
    Om du klickar på en post kopieras den till översättningsfältet.

interactivetour-InteractiveTour--locales-title = Lokaliseringar
interactivetour-InteractiveTour--locales-content =
    Ibland kan det vara användbart att se allmänna stilval från andra
    lokaliseringsgrupper. Godkända översättningar av den aktuella
    strängen till andra språk finns tillgängliga under fliken Lokaliseringar.

interactivetour-InteractiveTour--email-communications-title = Låt oss hålla kontakten
interactivetour-InteractiveTour--email-communications-content =
    Vill du hålla dig uppdaterad och informerad om alla lokaliseringsfrågor
    hos Mozilla? Aktivera e-postkommunikation från dina <a>inställningar</a> för att få
    de senaste uppdateringarna om lokalisering hos Mozilla, meddelanden om
    nya Pontoon-funktioner, inbjudningar till bidragsgivarevenemang och mycket mer.
interactivetour-InteractiveTour--email-communications-footer =
    (Se till att du är inloggad för att komma åt dina inställningar..)

interactivetour-InteractiveTour--end-title = Det är (inte) allt, gott folk!
interactivetour-InteractiveTour--end-content =
    Det finns en mängd olika verktyg som kan hjälpa dig med översättningar,
    varav vissa inte nämns i denna handledning. För fler
    ämnen av intresse för lokaliserare hos Mozilla, se
    <a>Localizer Documentation</a>.
interactivetour-InteractiveTour--end-footer =
    Därefter kan du gärna utforska det här handledningsprojektet eller gå direkt
    till <a>översättning av liveprojekt</a>.


## Machinery
## Shows a list of translations from machines.
machinery-Machinery--search-placeholder =
    .placeholder = Konkordanssökning

machinery-Machinery--load-more = LÄS IN FLER


## Machinery Caighdean Translation
## Shows the translation source from Caighdean Machine Translation.
machinery-CaighdeanTranslation--translation-source = CAIGHDEAN


## Machinery Concordance Search
## Shows concordance search results from Pontoon's memory.
machinery-ConcordanceSearch--translation-memory = ÖVERSÄTTNINGSMINNE


## Machinery Google Translation
## Shows the translation source from Google Translate.
machinery-GoogleTranslation--translation-source = GOOGLE TRANSLATE
machinery-GoogleTranslation--selector =
    .title = Förfina med hjälp av AI
machinery-GoogleTranslation--dropdown-title = AI

machinery-GoogleTranslation--option-rephrase = OMFORMULERA
machinery-GoogleTranslation--option-rephrased = OMFORMULERAD
machinery-GoogleTranslation--option-make-formal = GÖR FORMELL
machinery-GoogleTranslation--option-formal = FORMELL
machinery-GoogleTranslation--option-make-informal = GÖR INFORMELL
machinery-GoogleTranslation--option-informal = INFORMELL
machinery-GoogleTranslation--option-show-original = VISA ORIGINAL


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
    .title = Kopiera till översättning (Ctrl + Shift + Down)


## Machinery Translation Memory
## Shows the translation source from Pontoon's memory.
machinery-TranslationMemory--translation-source = ÖVERSÄTTNINGSMINNE
machinery-TranslationMemory--number-occurrences =
    .title = Antal översättningsförekomster


## Notification Messages
## Messages shown to users after they perform actions.

notification--translation-approved = Översättning godkänd
notification--translation-unapproved = Översättning inte godkänd
notification--translation-rejected = Översättning avvisad
notification--translation-unrejected = Översättning inte avvisad
notification--translation-deleted = Översättning borttagen
notification--translation-saved = Översättning sparad
notification--unable-to-approve-translation = Kunde inte godkänna översättning
notification--unable-to-unapprove-translation = Kunde inte avgodkänna översättning
notification--unable-to-reject-translation = Kunde inte avvisa översättning
notification--unable-to-unreject-translation = Kunde inte av-avvisa översättning
notification--unable-to-delete-translation = Kunde inte ta bort översättning
notification--same-translation = Samma översättning finns redan
notification--tt-checks-enabled = Translate Toolkit-kontroller aktiverade
notification--tt-checks-disabled = Translate Toolkit-kontroller inaktiverade
notification--make-suggestions-enabled = Gör förslag aktiverade
notification--make-suggestions-disabled = Gör förslag inaktiverade
notification--ftl-not-supported-rich-editor = Översättning stöds inte i avancerad redigerare
notification--entity-not-found = Kan inte läsa in angiven sträng
notification--string-link-copied = Länk kopierad till urklipp
notification--comment-added = Kommentar tillagd


## OtherLocales Translation
## Shows a specific translation from a different locale

otherlocales-Translation--copy =
    .title = Kopiera till översättning (Ctrl + Shift + Down)

otherlocales-Translation--header-link =
    .title = Öppna sträng i { $locale } ({ $code })


## Message terms
## Used to mark specific terms and characters in translations.

highlight-cli-option =
    .title = Kommandoradsalternativ
highlight-email =
    .title = E-post
highlight-escape =
    .title = Escape-sekvens
highlight-newline =
    .title = Nyradstecken
highlight-number =
    .title = Tal
highlight-placeholder =
    .title = Platshållare
highlight-placeholder-entity =
    .title = HTML/XML-entitet
highlight-placeholder-html =
    .title = HTML-tagg
highlight-placeholder-printf =
    .title = Printf-formatsträng
highlight-punctuation =
    .title = Interpunktion
highlight-spaces =
    .title = Ovanligt mellanrum
highlight-tab =
    .title = Tabb-tecken
highlight-url =
    .title = URL


## Project menu
## Used in the project menu in the main navigation bar.
project-ProjectMenu--no-results = Inga resultat
project-ProjectMenu--project = PROJEKT
project-ProjectMenu--progress = FÖRLOPP
project-ProjectMenu--all-projects = Alla projekt
project-ProjectMenu--search-placeholder =
    .placeholder = Filtrera projekt


## Resource menu
## Used in the resource menu in the main navigation bar.
resource-ResourceMenu--no-results = Inga resultat
resource-ResourceMenu--resource = RESURS
resource-ResourceMenu--progress = FÖRLOPP
resource-ResourceMenu--all-resources = Alla resurser
resource-ResourceMenu--all-projects = Alla projekt
resource-ResourceMenu--search-placeholder =
    .placeholder = Filtrera resurser


## Filters Panel
## Shows a list of filters, used to filter the list of entities.
search-FiltersPanel--heading-status = ÖVERSÄTTNINGSSTATUS
search-FiltersPanel--heading-tags = TAGGAR
search-FiltersPanel--heading-extra = EXTRAFILTER
search-FiltersPanel--heading-authors = UPPHOVSPERSONER FÖR ÖVERSÄTTNING
search-FiltersPanel--status-name-all = Alla
search-FiltersPanel--status-name-translated = Översatta
search-FiltersPanel--status-name-pretranslated = Förhandsöversatta
search-FiltersPanel--status-name-warnings = Varningar
search-FiltersPanel--status-name-errors = Fel
search-FiltersPanel--status-name-missing = Saknas
search-FiltersPanel--status-name-unreviewed = Ogranskade
search-FiltersPanel--extra-name-unchanged = Oförändrade
search-FiltersPanel--extra-name-empty = Tomma
search-FiltersPanel--extra-name-fuzzy = Luddiga
search-FiltersPanel--extra-name-rejected = Avvisade
search-FiltersPanel--extra-name-missing-without-unreviewed = Saknas förutom ogranskade

search-FiltersPanel--clear-selection = <glyph></glyph>CLEAR
    .title = Avmarkera valda filter

search-FiltersPanel--apply-filters =
    <glyph></glyph>TILLÄMPA <stress>{ $count }</stress> { $count ->
        [one] FILTER
       *[other] FILTER
    }
    .title = Tillämpa valda filter


## Search Options Panel

search-SearchPanel--option-name-search-match-case = Matcha skiftläge
search-SearchPanel--option-name-search-match-whole-word = Matcha hela ord
search-SearchPanel--option-name-search-identifiers = Sök i strängidentifierare
search-SearchPanel--option-name-search-rejected-translations = Inkludera avvisade översättningar
search-SearchPanel--option-name-search-exclude-source-strings = Exkludera källsträngar

search-SearchPanel--heading = SÖKALTERNATIV

search-SearchPanel--apply-search-options = TILLÄMPA SÖKALTERNATIV
    .title = Tillämpa valda sökalternativ

## Time Range Filter
## Time Range filter title, input fields and chart.

search-TimeRangeFilter--heading-time = ÖVERSÄTTNINGSTID
search-TimeRangeFilter--edit-range = <glyph></glyph>REDIGERA INTERVALL
search-TimeRangeFilter--save-range = SPARA INTERVALL


## Term
## Shows term entry with its metadata

term-Term--copy =
    .title = Kopiera till översättning

term-Term--for-example = T.EX.


## User Avatar
## Shows user Avatar with alt text

user-UserAvatar--anon-alt-text =
    .alt = Anonym användare
user-UserAvatar--alt-text =
    .alt = Användarprofil

## User Menu
## Shows user menu entries and options to sign in or out.

user-SignIn--sign-in = Logga in
user-SignOut--sign-out = <glyph></glyph>Logga ut

user-UserMenu--appearance-title = Välj utseende
user-UserMenu--appearance-dark = <glyph></glyph> Mörk
    .title = Använd ett mörkt tema
user-UserMenu--appearance-light = <glyph></glyph> Ljus
    .title = Använd ett ljust tema
user-UserMenu--appearance-system = <glyph></glyph> System
    .title = Använd ett tema som matchar dina systeminställningar

user-UserMenu--download-terminology = <glyph></glyph>Hämta ner terminologi
user-UserMenu--download-tm = <glyph></glyph>Hämta ner översättningsminne
user-UserMenu--download-translations = <glyph></glyph>Hämta ner översättningar
user-UserMenu--upload-translations = <glyph></glyph>Skicka upp översättningar

user-UserMenu--terms = <glyph></glyph>Användarvillkor
user-UserMenu--github = <glyph></glyph>Hacka det på GitHub
user-UserMenu--feedback = <glyph></glyph>Ge återkoppling
user-UserMenu--help = <glyph></glyph>Hjälp

user-UserMenu--admin = <glyph></glyph>Admin
user-UserMenu--admin-project = <glyph></glyph>Admin · Aktuellt projekt
user-UserMenu--sync-log = <glyph></glyph>Synkronisera logg

user-UserMenu--settings = <glyph></glyph>Inställningar


## User Notifications
## Shows user notifications menu.

user-UserNotificationsMenu--no-notifications-title = Inga nya aviseringar.
user-UserNotificationsMenu--no-notifications-description = Här ser du uppdateringar för lokaliseringar som du bidrar till.
user-UserNotificationsMenu--see-all-notifications = Se alla aviseringar


## Project Info
## Shows information of all projects

projectinfo-ProjectInfo--project-info-title = PROJEKTINFO
