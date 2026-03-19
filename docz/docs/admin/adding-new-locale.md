# Adding a New Locale

This page explains how to add a new language/locale to Pontoon. The example used throughout is Amharic (`am`).

## Step 1 — Add the locale in Django admin

Access Django's admin interface at `/a/` (not the standard `/admin/`), then click **Locales**.

Search for the locale you want to add (searching by locale code is safer). If the locale is not yet in Pontoon, click **ADD LOCALE+** in the top-right corner.

Complete the following fields:

### Core fields

| Field | Example | Notes |
|---|---|---|
| **Code** | `am` | The locale code (BCP 47). |
| **Name** | `Amharic` | The language name displayed in Pontoon. |
| **Plural rule** | *(see below)* | The Gettext plural rule expression. |
| **Cldr plurals** | `1,5` | Comma-separated list of available CLDR plural categories (no spaces). |

### Machine translation fields

| Field | Notes |
|---|---|
| **Google translate locale** | Google's locale code for this language. Leave blank to disable Google Translate for this locale. See [Google's supported locales list](https://cloud.google.com/translate/docs/languages). |
| **Google automl model** | Google AutoML model ID (usually starts with `NM`). Set after training a custom model (see [Managing Pretranslation](managing-pretranslation.md)). |
| **MS translator locale** | Microsoft Translator's locale code. Leave blank to disable. |
| **MS terminology locale** | Microsoft Terminology locale code. Leave blank to disable. |

### Plural rules

Look up the locale on [CLDR](https://www.unicode.org/cldr/charts/latest/supplemental/language_plural_rules.html). For Amharic, two cardinal plural forms are listed: `one` and `other`.

The **Gettext plural rule** is a C expression. For Amharic:
```
nplurals=2; plural=(n > 1);
```

The **CLDR plurals** field uses numbers corresponding to plural categories:
`0`=zero, `1`=one, `2`=two, `3`=few, `4`=many, `5`=other.

For Amharic (`one`, `other`) → `1,5`.

Irish (`ga-IE`) has all forms except zero → `1,2,3,4,5`.

### Access keys

Access keys allow keyboard-activated menu commands (shown as underlined characters).

- **Access key attribute checkbox checked** (default) — Pontoon leaves the access key field empty and shows a dynamic UI for translators to pick from available characters in the localized label. For pretranslation, it uses the first character of the pretranslated label.
- **Access key attribute checkbox unchecked** — Pontoon automatically uses the same access key as the source string (useful for locales using non-Latin scripts like Chinese or Japanese).

## Step 2 — Set up the Terminology project

The "Terminology" project appears automatically under the new team's page (e.g., `pontoon.mozilla.org/am/`) after the locale is saved.

## Step 3 — Populate CLDR population data (optional)

A helper script is available to assist with population data. Save the script as `cldr_population.py` and run:

```bash
python cldr_population.py LOCALE_CODE
```

## Step 4 — Enable pretranslation (optional)

Once the locale is added, you can set up a custom AutoML model and enable pretranslation. See [Managing Pretranslation](managing-pretranslation.md).
