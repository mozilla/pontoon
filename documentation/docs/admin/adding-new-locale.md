# Adding a New Locale

## Verify if the locale is already available

Access Django’s admin interface at `https://pontoon.mozilla.org/a/` (note that this is not the usual admin interface), then click `Locales`. In the next page search for the locale you want to add (safer to search for the locale code).

## Add the new locale

If the locale you need is not available, click the **ADD LOCALE+** button in the top right corner. For this example, let’s consider that the task is to add Amharic (am).

You will need to complete the following fields in the next page.

### Code

It’s the locale code, in this case `am`.

### Google Translate code

Google Translate maintains a list of supported locales in its own format. Choose one that matches the locale from [a list of supported locales](https://translate.google.com/intl/en/about/languages/) or leave it blank to disable support for Google Translate for this locale.

### Google AutoML model

Set your [Google Cloud AutoML Translation](https://cloud.google.com/translate/) model ID to use the custom translation engine with a trained model. You can find the model ID in [Google Cloud management console](https://console.cloud.google.com/translation/models/list). If the value is not set, Google’s generic machine translation technology is used instead.

### MS translator code

Microsoft Translator maintains a list of supported locales in its own format. Choose one that matches the locale from [a list of supported locales](https://docs.microsoft.com/azure/cognitive-services/Translator/language-support) or leave it blank to disable support for Microsoft Translator for this locale.

### MS terminology code

Microsoft Terminology maintains a list of supported locales in its own format. Choose one that matches the locale from a list provided below the field or leave it blank to disable support for Microsoft Terminology for this locale.

### Name

It’s the language name, in this case `Amharic`.

### Plural rule

It’s the GetText plural rule. This [document](http://docs.translatehouse.org/projects/localization-guide/en/latest/l10n/pluralforms.html) has plural rules for several languages. For example, for Amharic it would be:

```
nplurals=2; plural=(n > 1);
```

As explained in the note below the field, you only need to put the last part in the field:

```
(n > 1)
```

### CLDR Plurals

You need to find the locale on [CLDR](https://unicode-org.github.io/cldr-staging/charts/latest/supplemental/language_plural_rules.html). For Amharic, there are only two **cardinal** plural forms listed: one, other.

The mapping is:

```
0 -> zero
1 -> one
2 -> two
3 -> few
4 -> many
5 -> other
```

For Amharic you will need to set the field as `1,5`, separating the available forms with a comma (no spaces).

Irish (ga-IE), for example, has all of them except for 0, so it will be `1,2,3,4,5`.

### Script

The script used by this locale. Find it in [CLDR Languages and Scripts](http://www.unicode.org/cldr/charts/latest/supplemental/languages_and_scripts.html).

### Direction

Writing direction of the script. Set to `right-to-left` if `rtl` value for the locale script is set to `YES` in [CLDR scriptMetadata.json](https://github.com/unicode-cldr/cldr-core/blob/master/scriptMetadata.json).

### Population

This represents the number of native speakers. There are two ways to get this information from CLDR.

#### Using a script

Python needs to be available on the method to use this system: save [this file](https://raw.githubusercontent.com/mozilla-l10n/documentation/main/scripts/cldr_population.py) on your computer as `cldr_population.py` and run it as `python cldr_population.py LOCALE_CODE`.

For example, this is the output of the script when checking data for `sl`:

```
$ python scripts/cldr_population.py sl

Adding HU: 4937 (0.05% of 9874780)
Adding IT: 105412 (0.17% of 62007500)
Adding SI: 1720886 (87% of 1978030)
Adding AT: 32233 (0.37% of 8711770)
--------
Territories: AT, HU, IT, SI
Population: 1863468
--------
```

#### Manual process

Find the locale code in [CLDR territoryInfo.json](https://github.com/unicode-cldr/cldr-core/blob/master/supplemental/territoryInfo.json) and multiply its `_populationPercent` with the territory `_population`. Repeat if multiple occurrences of locale code exist and sum products.

At this point click **SAVE** in the bottom right corner to save and create the new locale. The "Terminology" project should appear automatically under the new team’s page — in this case at https://pontoon.mozilla.org/am/

### Access key localization

In software, access keys allow users to activate a menu command using their keyboard, and they’re displayed as an underlined character in the menu label. Some locales, especially those using a script different than Latin (Chinese, Japanese, etc.), don’t localize access keys, and use the same character as English. In this case, the access key will be appended to the label as an underlined character between parentheses.

Pontoon can recognize an access key attribute in Fluent strings, and provide translators with a dynamic UI to select one of the characters available in the localized label.

When the checkbox is selected (default), Pontoon will leave the access key field empty, and show the dynamic UI when translating. For pretranslation, it will use the first character from the pretranslated label.

When the checkbox is deselected, Pontoon will automatically use the same access key as the source string, for both manual translation and pretranslation.
