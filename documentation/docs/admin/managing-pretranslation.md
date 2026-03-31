# Managing Pretranslation

## Opt-in guidelines to enable new locales

It’s important to note that **these are not strict criteria**: members of staff will evaluate each request to opt in individually, based on their knowledge of the project and direct experience with the locale.

**Criteria for enabling pretranslation for a new locale**

* Request needs to come from translators or managers active within the last month (translating or reviewing).
* There is an active manager for the locale (last activity within 2 months).

**Criteria for enabling pretranslation for a new project**

* Less than 400 missing strings, except for projects or locales where existing pretranslation statistics provide high-confidence.
* Average review time for pretranslations in existing projects is faster than 3 weeks.

**Criteria for disabling the feature for a locale or a project**

* Approval rate drops below 40%.
* Average review time for pretranslations is slower than 6 weeks.

Note that disabling a project would always involve a conversation with reviewers for the locale.

## Enabling pretranslation in a project

Access Pontoon’s [admin console](https://pontoon.mozilla.org/admin/), and select the project: at the bottom of the page there is a section dedicated to *Pretranslation*.

**IMPORTANT**: if this is the first project for a locale, the first step is to [train and set up the custom machine translation model](#train-and-set-up-a-custom-machine-translation-model) in Google AutoML Translation.

Use the checkbox `PRETRANSLATION ENABLED` to enable the feature for the project, then move the requested locales from the `Available` list to `Chosen`. Clicking the `PRETRANSLATE` button will pretranslate immediately all missing strings in enabled locales, otherwise pretranslation will run automatically as soon as new strings are added to the project.

## Train and set up a custom machine translation model

To improve performance of the machine translation engine powering the pretranslation feature, custom machine translation models are trained for each locale using Pontoon’s translation memory. That results in better translation quality than what’s provided by the generic machine translation engine.

To create a custom translation model, first go to the [team page](https://mozilla-l10n.github.io/localizer-documentation/tools/pontoon/teams_projects.html#team-page) of the locale you are creating a custom translation model for and download its [translation memory file](https://mozilla-l10n.github.io/localizer-documentation/tools/pontoon/translate.html#downloading-and-uploading-translations). Next, go to the [Google Cloud console](https://console.cloud.google.com/translation/datasets?project=moz-fx-pontoon-prod) (requires permission) and follow these instructions — in case of doubt, consult the [official instructions](https://cloud.google.com/translate/automl/docs/create-machine-translation-model).

The first step is to create a translation dataset. In the `Datasets` panel, select `CREATE DATASET`:

* For the `Dataset name`, follow the pattern used by existing datasets: `dataset_LOCALE_YYYY_MM_DD` (e.g. `dataset_pt_BR_2023_09_20`, note that `-` is not allowed).
* Select the `Translate from…` language (`English (EN)`) and the `Translate to…` language (e.g. `Portuguese (PT)` for `pt-BR`).
* Click `CREATE`.

This operation will take a few seconds. At the end, an empty dataset with the selected name will be available in the list, with `0` in the `Total pairs` column. It’s now time to import Pontoon’s translation memory and train the model:

* Click the dataset, then navigate to the `IMPORT` tab.
* Use `SELECT FILES` to select the downloaded TMX file from your device.
* Click `BROWSE` in the `Destination on Cloud Storage` field and select `pontoon-prod-model-data-c1107144`.
* Click `CONTINUE` to start the import process. The import process will take a few minutes (it’s possible to close this window and return later to the list of datasets, when completed the `Status` column will say `Success: ImportData`).
* Once the import is completed, navigate to the `TRAIN` tab and click `START TRAINING`.

Note that creating the model is a background job which takes a few hours (when completed the `Status` column will say `Success: CreateModel`), and models for at most 4 locales can be trained concurrently. When the model is created, store its name (usually starting with `NM`, followed by a series of alphanumeric characters) under *Google automl model* in the [Django’s admin interface](https://pontoon.mozilla.org/a/) of the locale.

From that point on, Machinery will start using the custom machine translation model instead of the generic one and you’ll be set to enable pretranslation for the locale.
