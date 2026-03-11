# Developer Guide

[Pontoon](https://github.com/mozilla/pontoon) is a translation
management system used and developed by the Mozilla localization
community. It can handle any project that uses one of the supported file
formats:

-   .dtd
-   .ftl (Fluent)
-   .ini
-   .json (WebExtensions)
-   .json (key-value)
-   .po (Gettext)
-   .properties
-   .xliff
-   .xml (Android)

Pontoon pulls strings it needs to translate from an external source and
writes them back periodically. Typically these external sources are
version control repositories that store the strings for an application.
Supported external sources are **Git** and **Mercurial** repositories.

## Contributing

If you are interested in contributing to Pontoon\'s code, start with
`dev/first-contribution`{.interpreted-text role="doc"}.

## Deploying

If you want to deploy your own instance of Pontoon, read the
`admin/deployment`{.interpreted-text role="doc"} section.

Once you have a running instance, you will likely want to learn about
`user/localizing-your-projects`{.interpreted-text role="doc"}, and then
dive into [management
tasks](https://mozilla-l10n.github.io/documentation/tools/pontoon/).

## Localizing

If you\'re looking for help on using Pontoon for localizing projects,
whether on Mozilla\'s instance or any other, you can read our [How to
use
Pontoon](https://mozilla-l10n.github.io/localizer-documentation/tools/pontoon/)
documentation.

## Contents

::: {.toctree maxdepth="2"}
dev/first-contribution dev/setup dev/contributing
dev/feature-development-process admin/deployment admin/maintenance
user/localizing-your-projects dev/setup-virtualenv
:::
