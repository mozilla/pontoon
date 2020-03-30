- Feature Name: Terminology Presentation
- Created: 2020-03-24
- Associated Bug: https://bugzilla.mozilla.org/show_bug.cgi?id=1624557

# Summary

Terminology is a group of specialized words, compound words or multi-word expressions (terms) relating to a particular field. This feature adds the ability to store such terms in Pontoon, identify them in original strings and present them in the translation workbench.

# Motivation

- **Improving translation consistency**: it’s hard to expect all authors to always use the same translations for the same words and phrases without any help from the tool.
- **Speeding up translation process**: localizers need to manually search for existing translations of terms found in the strings they are translating.
- **Fixing brand translations**: trademarks present a special case for localization as they have legal and semantic significance, which isn't always obvious to localizers.
- **Advancing content comprehension**: it's not always clear what the (standard) expression means, especially if the comment isn't provided.

# Out of scope

- **Terminology creation**: the ability to manually add, remove and review terms.
- **Terminology translation**: the ability to manually add, remove and review term translations.
- **VCS integration**: the ability to sync terminology with VCS.
- **Checks**: the ability to check if translations include term translations.

# Feature explanation

As the first step, we need the ability to store terms in the database. Data model should allow for importing terms stored in a [TBX file](https://www.gala-global.org/sites/default/files/uploads/pdfs/tbx_oscar_0.pdf) and the [initial Mozilla term list](https://docs.google.com/spreadsheets/d/1MAPD8WBnstR6pwKbNEDKOpw5CTPnl3qAobDgomdmtdY/edit?ts=5e79126c#gid=1146590716).

The following information needs to be saved for each term:
- term itself
- review status (new, review, approved, obsolete)
- part of speech (verb, noun, adjective, adverb)
- definition
- usage example
- notes for term managers
- case sensitive (boolean, used when finding terms in strings)
- exact match (boolean, used when finding terms in strings)
- do not translate (boolean, used when translating terms)
- forbidden (boolean, note for developers)
- term translations (separate table)

Next, we need to identify stored terms in any original string used in translation workbench. We should take into account that terms can take various grammatical forms when used in strings and use tokenization and stemming to mitigate that.

Terms should be highlighted in the original string, similarly to how we highlight placeables. On term hover, a popup should appear with a list of matching terms and the corresponding metadata (part of speech, definition, translation). On click, translation of the first term in the list (if exists) should be inserted into the editor.

Additionally, we could also introduce the Terms panel in the 3rd column with the contents of the term popups of the entire string always visbile. On click, translation of the clicked term (if exists) should be inserted into the editor. Since this 3rd column is getting crowded with tabs, we should either split it vertically (as shown in the mockup) or (at least on narrow screens) replace tab titles with icons.

# Mockup

![](0101/mockup.png)
