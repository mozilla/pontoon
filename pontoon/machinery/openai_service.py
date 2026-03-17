import textwrap

from openai import OpenAI

from django.conf import settings
from django.core.cache import cache

from pontoon.base.models import Locale
from pontoon.machinery.utils import (
    get_machinery_service_cache_key,
    set_machinery_service_cache_key,
)


class OpenAIService:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("Missing OpenAI API key")
        self.client = OpenAI()

    def get_translation(
        self,
        english_text,
        translated_text,
        characteristic,
        target_language_name,
        string_id=None,
        string_comment=None,
        group_comment=None,
        resource_comment=None,
        pinned_comments=None,
        terms=None,
    ):
        terms_cache_key = (
            str(sorted((t.get("text", "") for t in terms))) if terms else ""
        )
        pinned_comments_cache_key = (
            str(sorted(pinned_comments)) if pinned_comments else ""
        )
        cache_key = get_machinery_service_cache_key(
            "openai_chatgpt",
            english_text,
            translated_text,
            characteristic,
            target_language_name,
            string_id or "",
            string_comment or "",
            group_comment or "",
            resource_comment or "",
            pinned_comments_cache_key,
            terms_cache_key,
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

        style_goals = {
            "informal": f"Use simple, everyday {target_language_name} ({target_language.code}) — avoid jargon, technical terms, and formal constructions.",
            "formal": f"Use formal {target_language_name} ({target_language.code}) throughout; maintain a consistent register and do not mix formal and informal modes.",
            "rephrased": f"Provide an alternative wording that preserves the original meaning; adapt idioms and culturally marked expressions for {target_language_name} ({target_language.code}); you may restructure sentences but must not introduce new information or omit essential meaning.",
        }

        style_goal = style_goals.get(characteristic)
        if style_goal is None:
            raise ValueError(f"Unrecognized characteristic: '{characteristic}'")

        # Separate the instruction from the data.
        # It makes it hard for injected text to masquerade as instructions.
        context_parts = []
        if string_id:
            context_parts.append(f"STRING ID:\n{string_id}")
        if resource_comment:
            context_parts.append(f"RESOURCE COMMENT:\n{resource_comment}")
        if group_comment:
            context_parts.append(f"GROUP COMMENT:\n{group_comment}")
        if string_comment:
            context_parts.append(f"STRING COMMENT:\n{string_comment}")
        if pinned_comments:
            pinned_block = "\n".join(f"- {c}" for c in pinned_comments)
            context_parts.append(f"PINNED COMMENTS:\n{pinned_block}")
        if terms:
            term_lines = []
            for term in terms:
                text = term.get("text", "")
                pos = term.get("part_of_speech", "")
                translation = term.get("translation", "")
                parts = [f'"{text}"']
                if pos:
                    parts.append(f"({pos})")
                if translation:
                    parts.append(f'→ "{translation}"')
                term_lines.append(" ".join(parts))
            terms_block = "\n".join(f"- {line}" for line in term_lines)
            context_parts.append(
                f"TERMINOLOGY:\nThese are terminology matches in the source text that you should consider:\n{terms_block}"
            )
        context_parts.append(f"ENGLISH SOURCE:\n{english_text}")
        context_parts.append(f"MACHINE TRANSLATION (for reference):\n{translated_text}")
        user_prompt = "\n\n".join(context_parts)

        system_header = textwrap.dedent(
            f"""\
            You are an expert {target_language_name} ({target_language.code}) localization specialist.

            Your task: produce a {characteristic} {target_language_name} ({target_language.code}) translation of a UI string.
            Use the provided machine translation as a reference, but you are not bound by it — rewrite freely to achieve the best result.
            """
        )

        context_instructions = []
        if string_id:
            context_instructions.append(
                "STRING ID: use it to infer the UI context (e.g., button, menu item, page title, tooltip) and adapt length and phrasing accordingly."
            )
        if resource_comment:
            context_instructions.append(
                "RESOURCE COMMENT: general notes about the file — use it as additional context."
            )
        if group_comment:
            context_instructions.append(
                "GROUP COMMENT: notes about the group of messages this string belongs to — use it as additional context."
            )
        if string_comment:
            context_instructions.append(
                "STRING COMMENT: treat it as authoritative translator notes — it may specify placeholders to preserve exactly, terms that must not be translated, or other constraints. STRING COMMENT requirements take precedence over all stylistic choices."
            )
        if pinned_comments:
            context_instructions.append(
                "PINNED COMMENTS: this is a comment added by a project manager — treat them as high-priority guidance from the localization team."
            )
        if terms:
            context_instructions.append(
                "TERMINOLOGY: use the given translations for those terms consistently in your output, unless you believe the existing translation to be incorrect for the context."
            )
        context_block = (
            "\n".join(context_instructions) + "\n\n" if context_instructions else ""
        )

        system_rules = textwrap.dedent(
            f"""\
            Your goal is to produce a natural, grammatically correct translation. Follow these rules strictly; if rules conflict, earlier rules take priority.
            1) ENDING PUNCTUATION — PRESERVE SEMANTICS
                - Determine the ending punctuation of the English source text (ignore trailing spaces and HTML tags).
                - The translation MUST end with the equivalent punctuation. Both directions are hard constraints:
                    • English ends with "." → translation MUST end with "." (or target-language equivalent)
                    • English ends with "?" → translation MUST end with a question mark
                    • English ends with "!" → translation MUST end with an exclamation mark
                    • English ends with "…" → translation MUST end with an ellipsis
                    • English has NO ending punctuation → translation MUST NOT end with ".", "?", "!", or "…"
                - Apply correct punctuation conventions for the target language (e.g. Spanish "¿ ¡", French non-breaking space before "?", "!", ":").
            2) HTML TAGS
                - Preserve all HTML tags exactly as in the source:
                    - Do not add, remove, reorder, or modify tags or attributes
                - Translate only the text content between tags, or the attributes if they contain translatable text (e.g., "alt", "title").
                - Keep punctuation placement consistent with the source structure (do not move punctuation across tag boundaries unless required by the target language grammar).
            3) {style_goal}

            Output only the translation, with no explanation."""
        )

        system_message = system_header + context_block + system_rules

        # TODO: remove before merge.
        # Print the full prompt before sending to help with debug.
        if settings.DEBUG:
            print(
                f"[OpenAI] system:\n{system_message}\n\n[OpenAI] user:\n{user_prompt}"
            )

        # Call the OpenAI API with the constructed prompt
        response = self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,  # Set temperature to 0 for deterministic output
            top_p=1,  # Set top_p to 1 to consider the full distribution
        )

        result = response.choices[0].message.content.strip()
        set_machinery_service_cache_key(cache_key, result)
        return result
