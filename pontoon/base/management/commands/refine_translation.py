from django.core.management.base import BaseCommand
from pontoon.gpt.openai_connection import OpenAIService


class Command(BaseCommand):
    help = "Refines machine translations using OpenAI with specified characteristics"

    def add_arguments(self, parser):
        parser.add_argument(
            "characteristic",
            type=str,
            choices=["informal", "formal", "alternative"],
            help="The specified characteristic of the translation (informal, formal, alternative)",
        )
        parser.add_argument(
            "english_text", type=str, help="The source string in English"
        )
        parser.add_argument(
            "target_text", type=str, help="The machine-generated translation to refine"
        )
        parser.add_argument(
            "locale_name",
            type=str,
            help="The name of the target locale for the translation",
        )

    def handle(self, *args, **options):
        characteristic = options["characteristic"]
        english_text = options["english_text"]
        target_text = options["target_text"]
        locale_name = options["locale_name"]

        translator = OpenAIService()
        translation = translator.get_translation(
            english_text, target_text, characteristic, locale_name
        )
        self.stdout.write(self.style.SUCCESS(translation))
