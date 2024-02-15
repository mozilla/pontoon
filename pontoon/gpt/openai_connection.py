from openai import OpenAI


class OpenAIService:
    def __init__(self):
        self.client = OpenAI()

    def get_translation(self, english_text, slovenian_text, formality):
        # Define system messages for different translation tasks
        system_messages = {
            "informal": """You will be provided with a passage in English, along with its machine-generated translation in Slovenian. Your objective is to revise the Slovenian translation to ensure it utilizes simpler language. Please adhere to the following guidelines to achieve this:
                    - Simplify Vocabulary: Use common, everyday words that are easily understood by a broad audience, avoiding technical jargon, idiomatic expressions, and complex terms.
                    - Shorten and Simplify Sentences: Break down long, complex sentences into shorter, more manageable ones. Aim for clarity and conciseness in each sentence.
                    - Use Basic Grammar Structures: Avoid complex grammatical constructions. Stick to simple tenses and straightforward sentence structures.
                    - Clarity is Key: Ensure the translation conveys the original message in the clearest possible manner, without ambiguity or unnecessary complexity.
                    - Engage a Wide Audience: The simplified translation should be accessible and easily understandable to people with varying levels of Slovenian proficiency, including young readers and non-native speakers.
                    - Consistent Simplicity: Maintain a consistent level of simplicity throughout the translation. The aim is to make the text as accessible as possible without sacrificing accuracy or meaning.
                    The goal is to produce a translation that accurately reflects the original English text, but in a way that is more approachable and easier to understand for all Slovenian speakers, regardless of their language proficiency.""",
            "formal": """You will be presented with text in English, accompanied by its machine-generated translation in Slovenian. Your task is to refine the Slovenian translation to ensure it adheres to a higher level of formality. In doing so, consider the following guidelines:
                    - Upgrade Language Use: Elevate the language by selecting more sophisticated vocabulary and phrases that are appropriate for formal contexts.
                    - Adjust the Tone: Ensure the tone is respectful, polished, and devoid of colloquialisms or informal expressions commonly used in casual conversation.
                    - Formal Addressing: Where applicable, use formal modes of address.
                    - Syntax and Structure: Pay attention to sentence structure, opting for more complex constructions that are typical in formal writing.
                    - Consistency: Maintain a consistent level of formality throughout the translation, avoiding shifts in tone or style.
                    - Cultural Sensitivity: Be mindful of cultural nuances that may affect the perception of formality in Slovenian.
                    Your goal is to produce a translation that not only accurately conveys the meaning of the English text but also meets the expectations for formality in Slovenian-speaking professional or formal settings.""",
            "alternative": """You will receive text in English along with its machine-generated translation in Slovenian. Your task is to provide an alternative translation, considering the following guidelines:
                    - Cultural Nuances: Pay attention to cultural nuances and idiomatic expressions, ensuring they are appropriately translated for the Slovenian-speaking audience.
                    - Clarification and Accuracy: Where the source text is ambiguous or idiomatic, offer clarifications or alternative expressions in Slovenian.
                    Just provide the text for the alternative translation.""",
        }

        system_message = system_messages.get(formality)

        if system_message is None:
            raise ValueError(f"Unrecognized formality type: '{formality}'")

        user_prompt = f"Original source string text: {english_text} Provided Slovenian machine translation: {slovenian_text}. {system_message}"

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
