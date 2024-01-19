- Feature Name: LLM-Assisted Translations in Pontoon
- Created: 2024-01-12
- Associated Issue: #3064

# Summary

Introduce LLM-assisted translations in Pontoon to provide alternative, formal, and informal translation options, enhancing translation quality.

# Motivation

Modern Large Language Models (LLMs) — like OpenAI’s GPT-4 — have reached a quality level for localization tasks that is on par with dedicated machine translation engines. This feature is primarily focused on introducing a tool that aims to improve translation quality in Mozilla's projects. By incorporating LLM-assisted translations, Mozilla not only remains competitive with other Translation Management Systems (TMS) providers but also embraces new technology to enhance the overall translation process. This feature also lays the groundwork for future integrations that could further enhance efficiency and broaden the scope of translation improvements within Mozilla's localization efforts.

# Feature explanation

In the Machinery tab of the Pontoon translate view, users will encounter a new dropdown option for each machine translation suggestion for a given string, offering three choices: 
1) `"Make Informal"` - Provide a more informal version of this translation 
2)  `"Make Formal"` - Provide a more formal version of this translation
3) `"Rephrase"` - Provide an alternative to this translation 

Upon selecting any of these options, the original machine translation will temporarily show `"AI is writing"` as the LLM generates the new translation. This revised translation will then appear in place of the original suggestion. Users can either accept or reject this new translation. Choosing 'accept' will directly replace the original machine translation with the new one. Each action will be followed by a confirmation pop-up.


# Implementation notes

The translation enhancement options will utilize OpenAI’s GPT-4 API to improve the existing machine translation suggestions. This is especially useful for accurately translating challenging phrases, like idiomatic expressions, by utilizing the LLM's capability to adapt translations to the specific style and nuances of the target language.

Additionally, data on the frequency of LLM usage and the adoption rate of LLM-provided translations will be collected to assess the tool's impact and refine its capabilities.

The implementation will be divided into several subtasks:
1. API integration to facilitate interaction between Pontoon and the GPT-4 API and logic to utilize translation memory as an input.
2. Implement the ability to provide alternative translation suggestions and to adjust translations for formality.
3. Frontend implementation for the new features.
4. Gather feedback, refine UI/UX, and fix any issues encountered.

# Mockup

![](0116/initial-drop-down.png)

*Initial drop-down menu*

![](0116/collapsed-drop-down.png)

*Collapsed drop-down menu*

![](0116/rephrase-selected.png)

*"Rephrase" option is selected*

![](0116/accept-or-reject.png)

*User can accept or reject the selection*

![](0116/confirmation.png)

*Confirmation pop-up*

![](0116/updated-translation.png)

*Updated translation*


