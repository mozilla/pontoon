- Feature Name: Documentation Overhaul
- Created: 2020-02-20
- Associated Bug: https://bugzilla.mozilla.org/show_bug.cgi?id=1616869

# Summary

Rebuild Pontoon's documentation to make it more accessible, more exhaustive and easier to maintain.

# Motivation

Pontoon's documentation is incomplete, sometimes out-dated, and spread out. Currently, we can find it on:

- Technical documentation - https://mozilla-pontoon.readthedocs.io/
- User documentation - https://mozilla-l10n.github.io/localizer-documentation/tools/pontoon/
- L10n drivers documentation - https://mozilla-l10n.github.io/documentation/tools/pontoon/

This might work to some extent for folks in the Mozilla community (thanks to l10n drivers knowing about this and being able to point users at the right places), but it is not easy to handle for external users, or people new to Pontoon.

It is also unclear who is responsible for maintaining these documentations. That can lead to big delays between a change in a feature and its associated documentation being updated.

# Feature explanation

## Target audiences

- **Localizer** — User of Pontoon wanting to learn how to efficiently translate and review projects. Looks for detailed feature documentation.
- **Administrator** — User of Pontoon wanting to learn how to manage projects and teams. Looks for detailed administration tasks documentation.
- **Project Owner** — Anyone wanting to make their project translated into several languages. Looks for internationalization and deployment documentation.
- **Developer** — A new developer wanting to make first contribution to Pontoon, or more experienced developer looking for technical documentation about code modules and development processes.

## How to organize

All documentation is put in one central place. It is organized by audience, with clearly defined sections, and an accessible front page allowing users to quickly find the documents they need.

A single place for all documentation means less questions about where to put what, and is easier to maintain.

## Where to store

Documentation is stored in the `docs` folder within the Pontoon code repository.

Having documentation in the same place as the code base allows us to enforce documentation updates along with code updates.

## Where to host

Documentation is hosted in a dedicated section within Pontoon app (`/docs`) and built on each deployment.

That's easier to set up for external deployments than using a 3rd party documentation service like ReadTheDocs. It also maps each Pontoon deployment to its corresponding documentation more explicitly, making sure deployment version and docs version match.

## What format to use

Documentation is writen using the Markdown syntax.

## Maintenance

TBD
