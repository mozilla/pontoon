from openai import OpenAI


class OpenAIService:
    def __init__(self):
        self.client = OpenAI()

    def get_translation(
        self, english_text, translated_text, characteristic, target_locale_name
    ):
        system_messages = {
            "informal": f"""You will be provided with text in English, along with its machine-generated translation in {target_locale_name}. Your objective is to revise the translation to ensure it utilizes simpler language. Please adhere to the following guidelines to achieve this:
                    - Clarity is Key: Ensure the translation conveys the original message in the clearest possible manner, without ambiguity or unnecessary complexity.
                    - Consistent Simplicity: Maintain a consistent level of simplicity throughout the translation.
                    The goal is to produce a translation that accurately reflects the original English text, but in a way that is more approachable and easier to understand for all {target_locale_name} speakers, regardless of their language proficiency.""",
            "formal": f"""You will be presented with text in English, accompanied by its machine-generated translation in {target_locale_name}. Your task is to refine the {target_locale_name} translation to ensure it adheres to a higher level of formality. In doing so, consider the following guidelines:
                    - Adjust the Tone: Ensure the tone is respectful, polished, and devoid of colloquialisms or informal expressions commonly used in casual conversation.
                    - Formal Addressing: Where applicable, use formal modes of address.
                    - Consistency: Maintain a consistent level of formality throughout the translation, avoiding shifts in tone or style.
                    Your goal is to produce a translation that not only accurately conveys the meaning of the English text but also meets the expectations for formality in {target_locale_name}-speaking professional or formal settings.""",
            "alternative": f"""You will receive text in English along with its machine-generated translation in {target_locale_name}. Your task is to provide an alternative translation, considering the following guidelines:
                    - Cultural Nuances: Pay attention to cultural nuances and idiomatic expressions, ensuring they are appropriately translated for the {target_locale_name}-speaking audience.
                    - Clarification and Accuracy: Where the source text is ambiguous or idiomatic, offer clarifications or alternative expressions in {target_locale_name}.
                    Just provide the text for the alternative translation.""",
        }

        system_message = system_messages.get(characteristic)
        if system_message is None:
            raise ValueError(f"Unrecognized characteristic: '{characteristic}'")

        # Construct the user prompt with the locale name
        user_prompt = f"Refine the following {target_locale_name} machine translation to make it {characteristic}: '{translated_text}' based on the original English text: '{english_text}'."

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

        # Extract the content attribute from the response
        translation = (
            response.choices[0].message.content
            if response.choices[0].message.content
            else ""
        )
        return translation.strip()
