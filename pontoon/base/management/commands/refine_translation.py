from django.core.management.base import BaseCommand
from pontoon.gpt.openai_connection import OpenAIService


class Command(BaseCommand):
    help = "Refines machine translations using OpenAI with specified formality"

    def add_arguments(self, parser):
        parser.add_argument(
            "formality",
            type=str,
            choices=["informal", "formal", "alternative"],
            help="The formality of the translation (informal, formal, alternative)",
        )
        parser.add_argument("english_text", type=str, help="The original English text")
        parser.add_argument(
            "slovenian_text",
            type=str,
            help="The machine-generated Slovenian translation to refine",
        )

    def handle(self, *args, **options):
        formality = options["formality"]
        english_text = options["english_text"]
        slovenian_text = options["slovenian_text"]

        translator = OpenAIService()
        translation = translator.get_translation(
            english_text, slovenian_text, formality
        )
        self.stdout.write(self.style.SUCCESS(translation))
