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

        informal = textwrap.dedent(
            f"""You will be provided with text in English, along with its machine-generated translation in {target_language}.
            Your objective is to revise the {target_language} translation to ensure it utilizes simpler language. Adhere to the following guidelines to achieve this:
            - Clarity is Key: Ensure the translation conveys the original message in the clearest possible manner, without ambiguity or unnecessary complexity.
            - Consistent Simplicity: Maintain a consistent level of simplicity throughout the translation.
            - Preserve All HTML Tags: Ensure that all HTML tags present in the original text are retained in the translation.
            - Avoid adding closing punctuation if it's not present in the original text.
            The goal is to produce a translation that accurately reflects the original English text, but in a way that is more approachable and easier to understand for all {target_language} speakers."""
        )

        formal = textwrap.dedent(
            f"""You will be provided with text in English, along with its machine-generated translation in {target_language}.
            Your objective is to revise the {target_language} translation to ensure it utilizes a higher level of formality. Adhere to the following guidelines to achieve this:
            - Adjust the Tone: Ensure the tone is respectful, polished, and devoid of colloquialisms or informal expressions commonly used in casual conversation.
            - Formal Addressing: Where applicable, use formal modes of address.
            - Consistency: Maintain a consistent level of formality throughout the translation, avoiding shifts in tone or style.
            - Preserve All HTML Tags: Ensure that all HTML tags present in the original text are retained in the translation.
            - Avoid adding closing punctuation if it's not present in the original text.
            Your goal is to produce a translation that not only accurately conveys the meaning of the English text but also meets the expectations for formality in {target_language}-speaking professional or formal settings."""
        )

        rephrased = textwrap.dedent(
            f"""You will be provided with text in English, along with its machine-generated translation in {target_language}.
            Your objective is to provide an alternative translation. Adhere to the following guidelines to achieve this:
            - Cultural Nuances: Pay attention to cultural nuances and idiomatic expressions, ensuring they are appropriately translated for the {target_language}-speaking audience.
            - Clarification and Accuracy: Where the source text is ambiguous or idiomatic, offer clarifications or alternative expressions in {target_language}.
            - Preserve All HTML Tags: Ensure that all HTML tags present in the original text are retained in the translation.
            - Avoid adding closing punctuation if it's not present in the original text.
            Just provide the text for the alternative translation."""
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
