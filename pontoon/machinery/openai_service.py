import textwrap

from openai import OpenAI

from django.conf import settings
from django.core.cache import cache

from pontoon.base.models import Locale
from pontoon.machinery.utils import ext_api_cache_set, get_ext_api_cache_key


class OpenAIService:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("Missing OpenAI API key")
        self.client = OpenAI()

    def get_translation(
        self, english_text, translated_text, characteristic, target_language_name
    ):
        cache_key = get_ext_api_cache_key(
            "openai",
            english_text,
            translated_text,
            characteristic,
            target_language_name,
        )
        cached = cache.get(cache_key)
        if cached is not None:
            return cached

        try:
            target_language = Locale.objects.get(name=target_language_name)
        except Locale.DoesNotExist:
            raise ValueError(
                f"The target language '{target_language_name}' is not supported."
            )

        intro_text = f"Refine the {target_language} machine translation below to make it {characteristic}."

        common_rules = textwrap.dedent(
            """Follow these rules IN ORDER OF PRIORITY:
            1) ENDING PUNCTUATION — SEMANTICS, NOT LITERAL CHAR:
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
            f"""{intro_text}
            Revise the {target_language} translation to use simpler language.
            {common_rules}
            3) Clarity and Simplicity: keep wording straightforward and consistent.
            Output only the revised translation."""
        )

        formal = textwrap.dedent(
            f"""{intro_text}
            Revise the {target_language} translation to use a higher level of formality.
            {common_rules}
            3) Consistency: maintain a consistent level of formality throughout; do not mix formal and informal modes.
            4) Preserve all HTML tags and their order. Do not add, remove, or reorder tags.
            5) Clarity and Precision: keep wording clear and unambiguous while remaining formal.
            Output only the revised translation."""
        )

        rephrased = textwrap.dedent(
            f"""{intro_text}
            Provide an alternative translation that preserves the original meaning while varying the wording.
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

        # Separate the instruction from the data.
        # It makes it hard for injected text to masquerade as instructions.
        user_prompt = (
            f"{intro_text}\n\n"
            f"ENGLISH SOURCE:\n{english_text}\n\n"
            f"MACHINE TRANSLATION TO REFINE:\n{translated_text}"
        )

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

        result = response.choices[0].message.content.strip()
        ext_api_cache_set(cache_key, result)
        return result
