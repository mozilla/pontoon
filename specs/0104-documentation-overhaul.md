- Feature Name: Documentation Overhaul
- Created: 2020-02-20
- Associated Bug: https://bugzilla.mozilla.org/show_bug.cgi?id=1616869

# Summary

Rebuild Pontoon's documentation to make it more accessible, more exhaustive and easier to maintain.

# Motivation

Pontoon's documentation is incomplete, sometimes out-dated, and spread out. Currently, we can find it on:

- Technical documentation - https://mozilla-pontoon.readthedocs.io/
- User documentation - https://mozilla-l10n.github.io/localizer-documentation/tools/pontoon/
- l10n drivers documentation - https://mozilla-l10n.github.io/documentation/tools/pontoon/

This might work to some extent for folks in the Mozilla community (I assume thanks to drivers knowing about this and being able to point users at the right places), but it is not easy to handle for external users, or people new to Pontoon.

It is also unclear who is responsible for maintaining those documentations. That can lead to big delays between a change in a feature and its associated documentation being updated.

# Feature explanation

It is unclear yet what the proper way to handle documentation would be, so this document currently describes potential solutions, with pros and cons.

## Target audiences

- **Developer** — New developer looking to contribute to Pontoon's code base, or core developer. Wants accessible setup and contributing documentation, as well as processes and technical documentation.
- **System Administrator** — System administrator looking to host their own instance of Pontoon. Wants platform-specific setup documentation.
- **Localizer** — User of Pontoon looking to learn how to efficiently translate projects. Wants detailed features documentation.
- **Project Manager** — User of Pontoon looking to learn how to manage projects and locales. Wants detailed administration tasks documentation.

## How to organize

### All in one place

Put all documentation in a central place. Organize by audience, with clearly defined sections, and an accessible front page allowing users to quickly find the documents they need.

**Pros**

- A single place for all documentation, meaning less questions about where to put what, and easier to maintain.
- If in the Pontoon repo, makes it easier to check that documentation is updated alongside features.

**Cons**

- Localizers don't care about development / deployment documentation, and it might confuse them to see it.
- We want to localize some of the documentation (for localizers, mostly) but not necessarily the rest (developer / admin). It might make it confusing to people to have only half of the docs translated.

### Two documentations

Have a documentation about features of Pontoon and how to use them (for **localizers** and **managers**), and one about the technical aspects of Pontoon (**administrators**, **contributors** and **developers**).

**Pros**

- Each audience has a more focused documentation, with less risks of confusion.
- Allows us to translate only the localizer-facing documentation, and not the technical one.

**Cons**

- Two distinct documentations to maintain, which is more difficult.
- There might be confusion about what to put where.

## Where to store documentation

### ReadTheDocs

We build the documentation automatically and push it to a readthedocs.org page on each update to the master branch.

**Pros**

- Hosted with Pontoon's code base, allowing to enforce documentation updates along with code changes.
- Localization is technically possible, but I don't know how difficult it would be.
- Easy to deploy and maintain, as ReadTheDocs is a mature solution and we have experience with it.

**Cons**

- Contributing to the documentation is difficult as it requires making a pull request on GitHub.

### Pontoon

We create our own documentation section directly in the Pontoon website.

**Pros**

- Hosted with Pontoon's code base, allowing to enforce documentation updates along with code changes.
- Localization requires a custom solution, making it easier because we can do exactly what fits us.
- Documentation is right there with Pontoon, making it super easy to find and integrate in the website.
- External users of Pontoon could customize the documentation based on their needs.

**Cons**

- Contributing to the documentation is difficult as it requires making a pull request on GitHub.
- Requires building our own documentation solution, with localization support.

### Wiki

**Pros**

- Very easy to edit, by anyone interested in doing so.
- Some wikis support content localization out of the box.

**Cons**

- High risk of having documentation out-of-sync with features, as it is more difficult to enforce developers update it when making changes to Pontoon.
- It is less clear who is responsible to update documentation.
- Requires deploying and maintaining a custom wiki somewhere.
- Requires content to be moderated in a different tool than GitHub.
