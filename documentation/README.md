# Pontoon Documentation

This folder contains the unified Pontoon documentation site, built with [Material for MkDocs](https://squidfunk.github.io/mkdocs-material/).

It consolidates three previously separate documentation sites:

| Audience | Previous location |
|---|---|
| Developers | `docs/` (ReadTheDocs / Sphinx) |
| Localizers | [mozilla-l10n/localizer-documentation](https://github.com/mozilla-l10n/localizer-documentation) |
| Admins | [mozilla-l10n/documentation](https://github.com/mozilla-l10n/documentation) |

## Structure

```
documentation/
├── mkdocs.yml              # MkDocs configuration
├── requirements.txt        # Python dependencies for building
└── docs/
    ├── index.md            # Home page
    ├── stylesheets/
    │   └── extra.css       # Mozilla/Pontoon brand styles
    ├── assets/             # Logo and other static assets
    ├── localizer/          # Localizer guide
    │   ├── index.md
    │   ├── translate.md
    │   ├── translation-workspace.md
    │   ├── teams-projects.md
    │   ├── users.md
    │   ├── notifications.md
    │   ├── profile.md
    │   └── glossary.md
    ├── admin/              # Admin & Project Manager guide
    │   ├── index.md
    │   ├── adding-new-project.md
    │   ├── adding-short-term-project.md
    │   ├── adding-new-locale.md
    │   ├── managing-pretranslation.md
    │   ├── messaging-center.md
    │   ├── renaming-file.md
    │   ├── renaming-project.md
    │   ├── managing-users.md
    │   └── adding-terminology.md
    └── dev/                # Developer guide
        ├── index.md
        ├── first-contribution.md
        ├── setup.md
        ├── setup-virtualenv.md
        ├── contributing.md
        ├── feature-development-process.md
        ├── deployment.md
        ├── localizing-your-projects.md
        └── maintenance.md
```
