import textwrap

from dataclasses import dataclass

from openai import OpenAI

from django.conf import settings
from django.core.cache import cache

from pontoon.machinery.utils import (
    get_machinery_service_cache_key,
    set_machinery_service_cache_key,
)


@dataclass
class LLMTranslation:
    """Result of a single `OpenAIService.get_translation()` call.

    A cache hit costs nothing, so it counts towards how often a suggestion was
    shown but not towards spend; token counts are only set when the API was
    actually called.
    """

    text: str
    cache_hit: bool
    prompt_tokens: int | None = None
    completion_tokens: int | None = None


class OpenAIService:
    def __init__(self):
        if not settings.OPENAI_API_KEY:
            raise ValueError("Missing OpenAI API key")
        self.client = OpenAI()

    def get_translation(
        self,
        english_text,
        references,
        characteristic,
        locale,
        entity_key=None,
        entity_comment=None,
        group_comment=None,
        resource_comment=None,
        pinned_comments=None,
        terms=None,
    ) -> LLMTranslation:
        """
        :param references: Existing translations to give the model as reference,
            as a list of ``{"source": …, "text": …}`` dicts, in the order they
            should be presented. May be empty, in which case the model translates
            from the English source alone.
        """
        style_goals = {
            "informal": f"Use simple, everyday {locale.name} ({locale.code}) — avoid jargon, technical terms, and formal constructions.",
            "formal": f"Use formal {locale.name} ({locale.code}) throughout; maintain a consistent register and do not mix formal and informal modes.",
            "rephrased": f"Provide an alternative wording that preserves the original meaning; adapt idioms and culturally marked expressions for {locale.name} ({locale.code}); you may restructure sentences but must not introduce new information or omit essential meaning.",
        }

        style_goal = style_goals.get(characteristic)
        if style_goal is None:
            raise ValueError(f"Unrecognized characteristic: '{characteristic}'")

        # Separate the instruction from the data.
        # It makes it hard for injected text to masquerade as instructions.
        context_parts = []
        if entity_key:
            context_parts.append(f"STRING ID:\n{entity_key}")
        if resource_comment:
            context_parts.append(f"RESOURCE COMMENT:\n{resource_comment}")
        if group_comment:
            context_parts.append(f"GROUP COMMENT:\n{group_comment}")
        if entity_comment:
            context_parts.append(f"STRING COMMENT:\n{entity_comment}")
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
        # A single reference is rendered exactly as the machine translation was
        # before references became a list, so that refining one machine
        # translation keeps producing the prompt it always has.
        if len(references) == 1:
            context_parts.append(
                f"MACHINE TRANSLATION (for reference):\n{references[0]['text']}"
            )
        elif references:
            reference_block = "\n".join(
                f"- {r['source']}: {r['text']}" for r in references
            )
            context_parts.append(
                f"EXISTING SUGGESTIONS (for reference):\n{reference_block}"
            )
        user_prompt = "\n\n".join(context_parts)

        match len(references):
            case 0:
                reference_instruction = ""
            case 1:
                reference_instruction = "Use the provided machine translation as a reference, but you are not bound by it — rewrite freely to achieve the best result.\n"
            case _:
                reference_instruction = "Use the provided suggestions as references, but you are not bound by them — rewrite freely to achieve the best result.\n"

        system_header = (
            textwrap.dedent(
                f"""\
            You are an expert {locale.name} ({locale.code}) localization specialist.

            Your task: produce a {characteristic} {locale.name} ({locale.code}) translation of a UI string.
            """
            )
            + reference_instruction
        )

        context_instructions = []
        if entity_key:
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
        if entity_comment:
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

        cache_key = get_machinery_service_cache_key(
            "openai_chatgpt",
            settings.OPENAI_MODEL,
            system_message,
            user_prompt,
        )
        cached = cache.get(cache_key)
        if cached is not None:
            return LLMTranslation(text=cached, cache_hit=True)

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
        usage = getattr(response, "usage", None)
        return LLMTranslation(
            text=result,
            cache_hit=False,
            prompt_tokens=getattr(usage, "prompt_tokens", None),
            completion_tokens=getattr(usage, "completion_tokens", None),
        )
