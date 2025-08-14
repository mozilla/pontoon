import textwrap

from openai import OpenAI

from pontoon.base.models import Locale
from pontoon.settings.base import OPENAI_API_KEY


class OpenAIService:
    def __init__(self):
        if not OPENAI_API_KEY:
            raise ValueError("Missing OpenAI API key")
        self.client = OpenAI()

    def get_translation(
        self, english_text, translated_text, characteristic, target_language_name
    ):
        try:
            target_language = Locale.objects.get(name=target_language_name)
        except Locale.DoesNotExist:
            raise ValueError(
                f"The target language '{target_language_name}' is not supported."
            )

        common_rules = textwrap.dedent(
            """1) ENDING PUNCTUATION — SEMANTICS, NOT LITERAL CHAR:
                - Detect the English ending: none, ".", "?", "!", "…".
                - The translation MUST express the same ending SEMANTIC:
                    • if English ends with "?" → translation ends with a question.
                    • if English ends with "!" → translation ends with an exclamation.
                    • if English ends with "…" → translation ends with an ellipsis.
                    • if English has NO closing punctuation → translation MUST NOT end with ".", "?", "!", or "…".
                - Do not add a final period if the English has none.
                - Respect orthographic and typographic rules of the target language regarding punctuation, like using non-breaking spaces in French, adding opening "¿" or "¡" in Spanish, etc.
            2) Preserve all HTML tags and their order. Do not add, remove, or reorder tags."""
        )

        informal = textwrap.dedent(
            f"""You will be provided with text in English, along with its machine-generated translation in {target_language}.
            Revise the {target_language} translation to use simpler language,
            Follow these rules IN ORDER OF PRIORITY:
            {common_rules}
            3) Clarity and Simplicity: keep wording straightforward and consistent.
            Output only the revised translation."""
        )

        formal = textwrap.dedent(
            f"""You will be provided with text in English, along with its machine-generated translation in {target_language}.
            Revise the {target_language} translation to use a higher level of formality.
            Follow these rules IN ORDER OF PRIORITY:
            {common_rules}
            3) Consistency: maintain a consistent level of formality throughout; do not mix formal and informal modes.
            4) Preserve all HTML tags and their order. Do not add, remove, or reorder tags.
            5) Clarity and Precision: keep wording clear and unambiguous while remaining formal.
            Output only the revised translation."""
        )

        rephrased = textwrap.dedent(
            f"""You will be provided with text in English, along with its machine-generated translation in {target_language}.
            Provide an alternative translation that preserves the original meaning while varying the wording.
            Follow these rules IN ORDER OF PRIORITY:
            {common_rules}
            3) Cultural and Idiomatic Fit: adapt idioms and culturally marked expressions appropriately for {target_language}; you may restructure sentences but must not introduce new information or omit essential meaning.
            4) Clarity and Naturalness: ensure the result reads naturally and is easy to understand.
            Output only the alternative translation."""
        )

        system_messages = {
            "informal": informal,
            "formal": formal,
            "rephrased": rephrased,
        }

        system_message = system_messages.get(characteristic)
        if system_message is None:
            raise ValueError(f"Unrecognized characteristic: '{characteristic}'")

        # Construct the user prompt with the language name
        user_prompt = f"Refine the following {target_language} machine translation to make it {characteristic}: '{translated_text}' based on the original English text: '{english_text}'."

        # Call the OpenAI API with the constructed prompt
        response = self.client.chat.completions.create(
            model="gpt-4.1-2025-04-14",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,  # Set temperature to 0 for deterministic output
            top_p=1,  # Set top_p to 1 to consider the full distribution
        )

        return response.choices[0].message.content.strip()
