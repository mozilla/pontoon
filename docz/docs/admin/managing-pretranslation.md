# Managing Pretranslation

Pretranslation automatically translates new strings using translation memory (TM) and machine translation, saving results as *Pretranslated* strings that can be reviewed before going live.

When pretranslation is enabled for a locale+project combination and a new string is added to Pontoon:

1. Pontoon checks for a **100% TM match** — if found, it is used directly.
2. If no TM match exists, the **Google AutoML Translation** custom model for the locale is used.
3. The string is saved with the *Pretranslated* status.
4. For VCS projects, the pretranslation is stored in localized files outside Pontoon.

## Enabling pretranslation for a project

Access Pontoon's admin console → open the project → scroll to the **Pretranslation** section at the bottom of the page.

!!! important
    If this is the **first project** being enabled for a locale, you must first train and set up a custom AutoML model (see below) before enabling pretranslation.

1. Check **PRETRANSLATION ENABLED**.
2. Move the desired locales from the **Available** list to **Chosen**.
3. Optionally, click **PRETRANSLATE** to immediately pretranslate all missing strings for enabled locales. Otherwise, pretranslation runs automatically as new strings are added.

## Training a custom AutoML model

Custom models are trained per locale using Pontoon's translation memory, resulting in better quality than the generic Google Translate engine.

### Step 1 — Download the TM

Go to the **Team page** for the locale → **TM** tab → download the TMX file.

### Step 2 — Import the TM into Google AutoML

1. Open the [Google Cloud Console](https://console.cloud.google.com) (requires permission).
2. Navigate to **AutoML Translation** → **Datasets** → **CREATE DATASET**.
3. Import the TMX file:
   - Click **BROWSE** in the *Destination on Cloud Storage* field and select `pontoon-prod-model-data-c1107144`.
   - Click **CONTINUE** to start the import.
   - Wait for the Status column to show `Success: ImportData` (a few minutes; you can close the window and return).

### Step 3 — Train the model

1. Navigate to the **TRAIN** tab → click **START TRAINING**.
2. Training is a background job that takes **several hours**. At most 4 locale models can train concurrently.
3. Wait for the Status column to show `Success: CreateModel`.
4. Note the model name (usually starts with `NM`, followed by alphanumeric characters).

### Step 4 — Register the model in Pontoon

In Django's admin interface at `/a/` → **Locales** → find the locale → set the **Google automl model** field to the model name noted above.

From this point, the Machinery tab uses the custom model and pretranslation is ready to be enabled.
