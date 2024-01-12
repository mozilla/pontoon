- Feature Name: LLM-Assisted Translations in Pontoon
- Created: 2024-01-12
- Associated Issue: #3064

# Summary

Introduce LLM-assisted translations in Pontoon to provide alternative, formal, and informal translation options, enhancing the localization process and community health.

# Motivation

In the realm of machine translation, recent studies have highlighted the evolving capabilities of Large Language Models (LLMs). This feature aims to revitalize community engagement and improve the efficiency of localization in Mozilla's projects. Incorporating LLM-assisted translations keeps Mozilla competitive with other TMS providers, adopting new technology for better community health and more effective translation.

# Feature explanation

In the Machinery tab of the Pontoon translate view, users will encounter a new dropdown option for each 100% translation memory match for a given string, offering three choices: 
1) Provide an alternative to this translation
2) Provide a more formal version of this translation
3) Provide a more informal version of this translation 

These options will utilize OpenAI’s GPT-4 API to generate translations, particularly beneficial for phrases that do not traditionally translate well, such as idiomatic expressions. The feature will leverage the LLM's in-context learning for translations that resonate with the stylistic nuances of the target language. 

Additionally, data on the frequency of LLM usage and the adoption rate of LLM-provided translations will be collected to assess the tool's impact and refine its capabilities.

# Implementation notes

The implementation will be divided into several subtasks:
1. API integration to facilitate interaction between Pontoon and the GPT-4 API and logic to utilize translation memory as an input.
2. Implement the ability to provide alternative translation suggestions and to adjust translations for formality.
3. Frontend implementation for the new features.
4. Gather feedback, refine UI/UX, and fix any issues encountered.

# Mockup

TBD
