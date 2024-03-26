from openai import OpenAI
from pontoon.base.models import Locale
from django.conf import settings


class OpenAIService:
    def __init__(self):
        api_key = settings.OPENAI_API_KEY
        if not api_key:
            raise ValueError("Missing OpenAI api key")
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

        informal = (
            f"You will be provided with text in English, along with its machine-generated translation in {target_language}. "
            "Your objective is to revise the {target_language} translation to ensure it utilizes simpler language. Adhere to the following guidelines to achieve this:\n"
            "- Clarity is Key: Ensure the translation conveys the original message in the clearest possible manner, without ambiguity or unnecessary complexity.\n"
            "- Consistent Simplicity: Maintain a consistent level of simplicity throughout the translation.\n"
            "The goal is to produce a translation that accurately reflects the original English text, but in a way that is more approachable and easier to understand for all {target_language} speakers."
        )

        formal = (
            f"You will be provided with text in English, along with its machine-generated translation in {target_language}. "
            "Your objective is to revise the {target_language} translation to ensure it utilizes a higher level of formality. Adhere to the following guidelines to achieve this:\n"
            "- Adjust the Tone: Ensure the tone is respectful, polished, and devoid of colloquialisms or informal expressions commonly used in casual conversation.\n"
            "- Formal Addressing: Where applicable, use formal modes of address.\n"
            "- Consistency: Maintain a consistent level of formality throughout the translation, avoiding shifts in tone or style.\n"
            "Your goal is to produce a translation that not only accurately conveys the meaning of the English text but also meets the expectations for formality in {target_language}-speaking professional or formal settings."
        )

        alternative = (
            f"You will be provided with text in English, along with its machine-generated translation in {target_language}. "
            "Your objective is to provide an alternative translation. Adhere to the following guidelines to achieve this:\n"
            "- Cultural Nuances: Pay attention to cultural nuances and idiomatic expressions, ensuring they are appropriately translated for the {target_language}-speaking audience.\n"
            "- Clarification and Accuracy: Where the source text is ambiguous or idiomatic, offer clarifications or alternative expressions in {target_language}.\n"
            "Just provide the text for the alternative translation."
        )

        system_messages = {
            "informal": informal,
            "formal": formal,
            "alternative": alternative,
        }

        system_message = system_messages.get(characteristic)
        if system_message is None:
            raise ValueError(f"Unrecognized characteristic: '{characteristic}'")

        # Construct the user prompt with the language name
        user_prompt = f"Refine the following {target_language} machine translation to make it {characteristic}: '{translated_text}' based on the original English text: '{english_text}'."

        # Call the OpenAI API with the constructed prompt
        response = self.client.chat.completions.create(
            model="gpt-4-0125-preview",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,  # Set temperature to 0 for deterministic output
            top_p=1,  # Set top_p to 1 to consider the full distribution
        )

        return response.choices[0].message.content.strip()
