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

We need a new built-in translation project (called "Terminology"), which will allow for translation of all terms using the translation workbench. The project would be similar to system projects (e.g. "Tutorial") in that it would be enabled automatically for any locale and any newly added locale, but would (unlike system projects) remain visible in dashboards and included in team stats.

For every `Term` with the `do_not_translate` and `forbidden` field set to False, an `Entity` will be created in the "Terminology" project with the following data:
* `Entity.string` with content of `Term.text`.
* `Entity.comment` with joint content of `Term.part_of_speech`, `Term.definition` and `Term.usage`.

The project will be stored in the database (not repository) and will "sync" automatically with the `Term` and `TermTranslation` models. Whenever a `Term` is created, updated or deleted, that needs to be reflected in the corresponding `Entity` in the "Terminology" project. Similarly, whenever a `Translation` in the "Terminology" project is created, updated (e.g. reviewed) or deleted, we need to make the corresponding change in the `TermTranslation` model.

A link should be added to every term in the Terms panel and popup leading to the translate workbench to translate that specific term to the currently used locale.
