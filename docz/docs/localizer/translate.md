# How to Translate

This page describes how to translate and review strings in Pontoon, and provides an example of a typical team workflow.

## The editor

When you select a string in the sidebar, the translation editor appears in the center of the page. If the string already has a translation, the editor is pre-populated with the existing text for you to modify.

### Suggestion Mode vs Translation Mode

Your editing mode depends on your [permissions](users.md#roles-and-permissions):

**Suggestion Mode** — a blue **SUGGEST** button is shown. Used when:

- You are a Contributor (default for new users).
- You are a Translator or Team Manager who has manually enabled *Make suggestions* in settings.

Suggestions are stored only in the Pontoon database. They are not committed to the version control system (VCS) and do not appear in the translation memory until approved.

**Translation Mode** — a green **SAVE** button is shown. Available to Translators and Team Managers. When you save a translation:

- It is displayed below the editing space and in the sidebar.
- It is stored in the VCS (where applicable).
- All pending suggestions or pretranslations for that string are rejected.

!!! tip
    Even if you have permission to save translations directly, submitting suggestions for peer review is good practice and improves overall quality.

To manually switch to Suggestion Mode, click the **gear icon** in the lower-left of the editor and select **Make suggestions**.

## Submitting a translation

1. Select a string from the sidebar.
2. Type your translation in the editor.
3. Click **SUGGEST** (Suggestion Mode) or **SAVE** (Translation Mode).

## Quality checks

Pontoon automatically checks every translation or suggestion you submit for potential issues. There are two severity levels:

**Errors** — critical issues that would break the product (e.g., incorrect syntax, exceeding maximum string length). The submit button is hidden until the error is fixed.

**Warnings** — potential issues that may or may not cause problems. You can bypass warnings and submit anyway, but review them carefully first.

Failures are stored in the database and can be filtered from the search bar.

## Reviewing suggestions

If you have Translator permissions, you can review other contributors' suggestions:

- **Approve** a suggestion by clicking the green checkmark. The suggestion becomes a saved translation.
- **Reject** a suggestion by clicking the red X.
- After rejecting, you can **delete** it entirely using the trashcan icon.
- Alternatively, enable *Make suggestions*, edit the translation as appropriate, and click **SUGGEST** to add a corrected version.

For pretranslations, rejecting also removes the text from the VCS (where applicable).

## Downloading and uploading translations

Click the **profile icon** in the top-right corner of any page to access download and upload options. These are only visible when you are in the translation workspace.

- **Anyone** can download terminology (`.tbx`), translation memory (`.tmx`), and translations.
- **Translators** can also upload translations.

When downloading:

- The currently selected resource is downloaded in its original format.
- If the project has multiple files, a ZIP of all files is downloaded.
- If a project has more than 10 files, only the currently translated file is downloaded.

When uploading, translations that differ from Pontoon's current state are imported and attributed to you.

## Requesting context or reporting issues

If a source string is unclear, use the **REQUEST CONTEXT** or **REPORT ISSUE** feature to ask the Project Manager. This tags them in a comment on the string.

## Workflow example

The following describes a typical AB workflow (two-translator model), but can be adapted for a single-translator AA workflow or a multi-translator ABCn workflow.

### Phase 1 — Submit suggestions (Contributor / Translator in Suggestion Mode)

1. Log in to Pontoon.
2. Browse to the project.
3. Use filters to select **Missing** strings (missing translation, fuzzy, or containing errors).
4. Click the gear icon below the editor → enable **Make suggestions**.
5. For each string, type a translation and click **SUGGEST**.
6. If a string is unclear, use **REQUEST CONTEXT** or **REPORT ISSUE** to ask the Project Manager.
7. Use [Pontoon's translation tools](translation-workspace.md#machinery-tab) to ensure consistency and speed.

### Phase 2 — Review suggestions (Translator / Team Manager)

1. Log in to Pontoon.
2. Browse to the project.
3. Use filters to select **Unreviewed** strings.
4. For each suggestion:
   - If the translation is correct → click the green checkmark to **approve**.
   - If the translation needs changes → edit in the editor and click **SAVE**, or add a new suggestion.
   - If the translation is unacceptable → reject and optionally delete it.
