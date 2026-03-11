# Translation Workspace

The translation workspace is the main interface for translating strings in Pontoon. It is divided into three main areas: the **sidebar** (left), the **editor** (center), and the **tools panel** (right).

## Sidebar

The sidebar lists all strings in the currently selected resource, along with their status.

### String statuses

| Status | Description |
|---|---|
| **Translated** | Has an approved translation; saved to the localized file in VCS. |
| **Pretranslated** | Automatically translated but not yet reviewed; saved to VCS. |
| **Warnings** | Has a translation, but with non-critical quality check issues. |
| **Errors** | Has critical quality check issues. |
| **Missing** | No approved translation exists. |
| **Unreviewed** | Has suggested translations awaiting review; not in VCS. |

### Search

Use the search field to search within the currently selected project. Searches cover string text and string IDs, and they respect any active filters.

- By default, Pontoon matches strings containing **any** of the search terms.
- For an **exact match**, wrap terms in double quotes: `"new tab"`.
- To search for strings containing literal double quotes, escape them: `\"`.

**Additional search options** (click the magnifying glass icon):

- **Match case** — exact capitalization matching.
- **Match whole word** — avoids partial matches.

### Filters

Click the filter icon to filter strings by status. Filters can be combined with search.

### Context button

When a string is selected, a small icon with four arrows appears near the checkbox. Clicking it shows strings that surround the selected string in the resource, providing translation context.

## Editor

See [How to Translate](translate.md) for full details on the editor, suggestion mode, and translation mode.

### Read-only mode

Some locales may have read-only access to a project. Their translations are still visible in the LOCALES tab for other teams to reference, but it is not possible to submit or modify translations directly.

## Translation tools (right panel)

### Machinery tab

The Machinery tab shows possible translations from multiple sources:

- Pontoon's internal **translation memory** (all approved translations across all projects).
- **Google Translate**.
- **Microsoft Translator / Bing Translator** (availability varies by deployment).
- **Concordance search** — search across all projects in Pontoon by source or target language text.

!!! warning
    Use machinery suggestions with care. Even when source strings match, the context in different projects may be different, leading to incorrect or unnatural translations. Always prioritize the meaning and purpose of the string.

The number of entries is shown next to the **MACHINERY** heading. Translation memory matches appear separately in green.

### AI refinement

For locales with Google Translate enabled, an **AI** dropdown appears above the machinery suggestions. It refines the Google Translate output using a large language model and provides three options:

- **REPHRASE** — generates an alternative translation.
- **MAKE FORMAL** — generates a more formal version.
- **MAKE INFORMAL** — generates a simpler, more informal version.

After selecting an option, the revised translation replaces the original in the editor. A **SHOW ORIGINAL** option then becomes available to revert to the original suggestion.

### LOCALES tab

Shows translations of the current string in other locales enabled for the project. Useful for cross-language context, especially for locales with read-only access.

### COMMENTS tab

The Comments tab has two types of comments:

**Source string comments** — associated with the source string itself. These are displayed in the COMMENTS tab in the right column and are designed for team discussion about the string's meaning or context. Administrators can **pin** a comment to make it visible alongside the editing area as a **PINNED COMMENT**, and users will receive a notification.

**Translation comments** — associated with a specific translation, displayed under the editor in the translation list.

!!! note
    These are different from **Resource comments**, which are added by developers directly in the resource file and are displayed in the editing area alongside the resource path and context.

### Tags

Tags can be used in a project to logically group resources and assign them a priority. If tags are enabled for a project, a Tags tab appears in Team and Project pages. Resources can be filtered by tag in the sidebar.

## Translation history

Below the editor, a list of all past translations for the current string is shown, including:

- The translator's name, profile picture, and banner.
- How long ago the entry was submitted (hover for the exact date/time).
- The translation text.
- Status icons (approved, pretranslated, unreviewed, rejected).
- Translation comments.

## Keyboard shortcuts

| Action | Shortcut |
|---|---|
| Copy source string to editor | `Ctrl`+`Shift`+`C` |
| Submit translation / suggestion | `Ctrl`+`Enter` |
| Navigate to previous string | `Alt`+`↑` |
| Navigate to next string | `Alt`+`↓` |
| Navigate to previous unreviewed | `Alt`+`Shift`+`↑` |
| Navigate to next unreviewed | `Alt`+`Shift`+`↓` |
| Approve translation | `Alt`+`Enter` |
| Select all strings in sidebar | `Ctrl`+`Shift`+`A` |
| Open machinery tab | `Ctrl`+`Shift`+`M` |
| Open history tab | `Ctrl`+`Shift`+`H` |
| Open comments tab | `Ctrl`+`Shift`+`X` |
| Toggle find & replace | `Ctrl`+`H` |
