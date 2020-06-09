- Feature Name: Terminology Translation
- Created: 2020-04-24
- Associated Bug: https://bugzilla.mozilla.org/show_bug.cgi?id=1381959

# Summary

Add the ability to translate terminology.

# Motivation

As part of [bug 1624557](https://bugzilla.mozilla.org/show_bug.cgi?id=1624557) we've added the ability to store terminology in the database and use term translations during the translation process. However, localizers currently don't have the ability to translate terms, which means they only partially benefit from using terminology. They can see what terms mean and how they can be used in source strings, but since they aren't translated, translations need to be manually looked for.

# Out of scope

- **Terminology creation**: the ability to manually add, remove and review terms.
- **VCS integration**: the ability to sync terminology with VCS.
- **Checks**: the ability to check if translations include term translations.

# Feature explanation

The feature introduces a new built-in translation project, called "Terminology". It allows for translation of all terms using the translation workbench. The project is (similarly to system projects like "Tutorial") enabled automatically for all locales and all newly added locales, but (unlike system projects) remains visible in dashboards and included in team stats. Terminology Presentation features (Panel and Popup) are disabled for the project, because all the relevant data is already included in the comments.

Access to term translation is also possible through the Terms panel and popup. Every term on the list is linked to the "Terminology" project, where it can be translated to the current locale.

# Synchronization between translation project and data model

The "Terminology" project is stored in the database (not repository) and behind the scenes "syncs" with the `Term` and `TermTranslation` models, which are used for faster access to the terminology data (TranslationMemoryEntry serves a similar purpose). For every localizable `Term`, a corresponding `Entity` exists in the "Terminology" project according to the following rules:
* `Entity.string` contains content of `Term.text`.
* `Entity.comment` contains joint content of several fields: "`Term.part_of_speech`. `Term.definition`. E.g.: `Term.usage`.".

A `Term` is localizable if the `do_not_translate` and `forbidden` fields are set to False and the `definition` field has value.

The following changes are made in the "Terminology" project when the `Term` model changes:
* When a `Term` instance is created, a corresponding `Entity` instance gets created (or deobsoleted) and set as a ForeignKey of the `Term` instance according to the above rules.
* When a `Term` instance is deleted, a corresponding `Entity` instance becomes obsolete.
* When a `Term` instance is updated:
  * If `Term.text` changes, a new `Entity` instance gets created and the previous one becomes obsolete.
  * If `Term.part_of_speech`, `Term.definition` or `Term.usage` change, `Entity.comment` gets updated.
  * If term becomes localizable, a new `Entity` instance gets created.
  * If term changes to no longer be localizable, a corresponding `Entity` instance becomes obsolete.
* Stats are updated accordingly.

When an approved translation in the "Terminology" project changes (through submit, delete, review or batch action), the following changes are made in the `TermTranslation` model:
* If the approved translation previously didn't exist, a new `TermTranslation` instance is created with `TermTranslation.text` value set to `Translation.string` of the approved translation.
* If the approved translation previously existed, `TermTranslation.text` gets updated to become `Translation.string` of the approved translation.
* If the approved translation doesn't exist anymore, a corresponding `TermTranslation` instance gets deleted.
