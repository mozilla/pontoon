# Glossary

Key terms used throughout Pontoon and this documentation.

## Contributor
A user without translator permissions. Contributors can only submit **suggestions**, which must be reviewed and approved by a Translator or Team Manager before appearing in the product.

## Concordance search
A search feature in the Machinery tab that searches across **all projects** in Pontoon using either the source or target language. Results show the source string, translation, and project name; clicking a result fills the translation into the editor.

## Fuzzy
An internal state available only in Gettext (`.po`) files. A string may be marked fuzzy when:

- The source string changed after it was already translated.
- A translator manually marked it for review.
- New strings were merged into the localized files using the option to match existing translations.

Fuzzy strings are equivalent to "needs review" and are not used by the website or application.

## Locale
The combination of a language and a region, represented in Pontoon by a locale code. For example, American English is `en-US`, where `en` is the language and `US` is the region. In some cases, the region is omitted. Each locale in Pontoon maps to a **Team**.

## Pretranslation
An automated feature that uses **translation memory** (100% matches first) and **Google AutoML Translation** (a custom trained model) to automatically translate new strings. Pretranslated strings have the *Pretranslated* status and must be reviewed before they are considered final. For VCS projects, pretranslations are saved directly to localized files.

## Resource
A localization file within a repository used to store source content and translations. Resources generally follow a key-value structure where the key (displayed as *Context* in Pontoon) is a unique identifier and the value is the text to translate. Supported formats include Fluent, Gettext PO, XLIFF, `.properties`, DTD, and others.

## Suggestion
A translation submitted by a Contributor, or by a Translator/Manager who has enabled *Make suggestions*. A suggestion exists only in the Pontoon database — it is not committed to the VCS or added to the translation memory until approved.

## Sync
The process by which Pontoon periodically (typically every 10 minutes) pulls source strings and translations from VCS repositories and writes approved translations back. Sync keeps the Pontoon database and the repository in sync.

## TBX (TermBase eXchange)
A standard XML file format for exchanging **terminology** (glossary) data between translation tools.

## Terminology / Glossary
A curated list of terms and their definitions. Pontoon highlights recognized terms in source strings and shows their definitions and existing translations into the target language.

## TMX (Translation Memory eXchange)
A standard XML file format for exchanging **translation memory** data between translation tools. Pontoon's translation memory can be downloaded as a TMX file from any Team page.

## Translation memory (TM)
A database of all approved translations for any string in Pontoon. It is used as a suggestion source in the Machinery tab and powers the pretranslation feature. Translation memory can be downloaded as a TMX file.

## Translation Mode
The editing mode available to Translators and Team Managers in which a green **SAVE** button is displayed. Saving a translation approves it directly, commits it to VCS (where applicable), and rejects all pending suggestions.

## Suggestion Mode
The editing mode (default for Contributors; optionally enabled by Translators/Managers) in which a blue **SUGGEST** button is displayed. Submissions are stored as unreviewed suggestions.

## Translator
A user with permission to submit approved translations directly and to review suggestions. See [User Accounts & Settings](users.md#roles-and-permissions).

## Team Manager
A user who has Translator permissions and can also manage permissions for other users within their locale. See [User Accounts & Settings](users.md#roles-and-permissions).

## VCS (Version Control System)
The external system where source strings and translations are stored — typically a Git or Mercurial repository. Pontoon reads from and writes to VCS repositories as part of the Sync process.
