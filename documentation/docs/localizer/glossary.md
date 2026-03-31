# Glossary

Explanation of common terms and concepts used across documentation.

## Comment

Comments can be used, for example, to discuss possible translations with other team members or request more information from project managers.

Pontoon supports two types of user comments:

* *Source string comments* are associated with the source string and displayed in the `COMMENTS` tab in the right column.
* *Translation comments* are associated with a specific translation and displayed under the editor in the [translation list](translation_workspace.md#translation-list).

Comment authors can edit or delete their own comments. Project managers can also delete any comment for moderation purposes.

User comments should not be confused with *Resource comments*, which developers can add directly to the resource file. This type of comment is displayed in the editing area, along with other information like the [resource path and context](#resource).

## Fuzzy

`fuzzy` is an internal state available only if the source file is a [gettext](https://www.gnu.org/software/gettext/manual/html_node/PO-Files.html) (.po) file. A string can be marked as such in a few cases:

* The reference text changed after the string was already translated.
* The string has been manually marked by translators because it needs review.
* New strings were merged in the localized files, enabling the option to match existing translations (also called “fuzzy matching”).

In all these cases a translation exists in the file, but is marked as fuzzy (equivalent to “need review”) and not used by the website or application. For more information, read the documentation about [Fuzzy Entries](https://www.gnu.org/software/gettext/manual/html_node/Fuzzy-Entries.html#Fuzzy-Entries) in gettext.

## Locale

A locale is the combination of a language and a region, represented in Pontoon by a locale code. For example, American English is referred to as `en-US`, where `en` stands for the language (English), and `US` for the region (United States). In some cases, the region is omitted, because the language is mostly spoken in one region.

In Pontoon, each locale maps to a team.

## Permission

Users in Pontoon can have different permissions depending on their role:

* Translators can either submit approved translations directly or review suggestions from other users. Unlike in some other Translation Management Systems, this is a single permission in Pontoon, and it’s referred to as *Translator permission*.
* Team managers have translator permissions, but can also change permissions assigned to other users (i.e., ”promote” or ”demote” them).

## Pretranslation

Pretranslation is a feature in Pontoon that relies on machine translation ([Google AutoML Translation](https://cloud.google.com/translate/automl/docs)) and [translation memory](#translation-memory) to automatically translate strings and save them in localized files.

If pretranslation is enabled for a combination of a locale and a project, when a new string is added in Pontoon:

* It will be translated (pretranslated) using a 100% match from translation memory or, should that not be available, using the Google AutoML Translation engine with a custom model.
* The string will be stored in Pontoon with the *pretranslated* status.
* For projects using [version control systems](#version-control-system), the translation will be stored in localized files outside of Pontoon.

## Resource

Resources are localization files within a repository (see [version control system](#version-control-system)) used to store source content and translations. They can be in different file formats but generally follow the same key-value structure, where the key (displayed as `Context` in the Source string panel) is a unique identifier and the value is a text snippet that needs to be translated.

## Terminology

Terminology — sometimes also referred to as a *Glossary* — is a list of terms and their definitions. Pontoon will highlight any terms in the source string and show their definitions as well as translations into the target language.

`TBX`, or *TermBase eXchange*, is a standard file format used in the translation industry to represent and exchange terminological information. Pontoon Terminology can be downloaded in the `TBX` format.

## Translation

A translation is any submission of the target content. There are several types of translations:

* *Approved translations*: translations submitted directly or approved by users with translator permissions.
* *Suggestions*: translations that have not been reviewed yet (pending).
* *Pretranslations*: translations that have been authored by the pretranslation feature.

## Translation memory

Translation memory is a list of all approved translations for any string. It can be leveraged to provide suggestions when translating new content.

`TMX`, or *Translation Memory eXchange*, is a standard file format used in the translation industry to represent and exchange translation memories. Pontoon Translation memory can be downloaded in the `TMX` format.

## Translation mode

Depending on their settings and permissions, users will be able to submit translations directly (*Translation Mode*), or only submit suggestions (*Suggestion Mode*).

Contributors — users without translator permissions — can only access *Suggestion Mode*, while translators and team managers can manually switch between the modes.

## Version Control System

Most projects store source content and translations outside of Pontoon, in repositories that use [version control systems (VCS)](https://en.wikipedia.org/wiki/Version_control). The most popular are git and Mercurial (hg).

Pontoon periodically (usually every 10 minutes) imports source content and translations from these repositories and writes translations back. This process is referred to as *Sync*.

Pontoon also supports the so-called `DB projects`, where source content and translations are stored in Pontoon’s internal database (DB).
