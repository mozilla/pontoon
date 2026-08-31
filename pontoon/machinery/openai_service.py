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
class OpenAITranslation:
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
    ) -> OpenAITranslation:
        """
        :param references: Existing translations to give the model as reference,
            as a ``{source: [text, …]}`` mapping, in the order they should be
            presented. May be empty, in which case the model translates from the
            English source alone.
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
        # Flattened, because a source may contribute more than one text and the
        # prompt presents them as a flat list.
        flat_references = [
            (source, text) for source, texts in references.items() for text in texts
        ]
        match len(flat_references):
            case 0:
                reference_instruction = ""
            # A single reference is rendered exactly as the machine translation
            # was before references became a mapping, so that refining one
            # machine translation keeps producing the prompt it always has.
            case 1:
                context_parts.append(
                    f"MACHINE TRANSLATION (for reference):\n{flat_references[0][1]}"
                )
                reference_instruction = "Use the provided reference as a guide, but rewrite freely if it can be improved.\n"
            case _:
                reference_block = "\n".join(
                    f"- {source}: {text}" for source, text in flat_references
                )
                context_parts.append(
                    f"EXISTING SUGGESTIONS (for reference):\n{reference_block}"
                )
                reference_instruction = "Use the provided references as a guide, but rewrite freely if they can be improved.\n"

        user_prompt = "\n\n".join(context_parts)

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
                "STRING ID: infer the UI context (e.g. button, menu item, title, tooltip) and adapt length and phrasing accordingly."
            )
        if resource_comment:
            context_instructions.append(
                "RESOURCE COMMENT: background context about the file."
            )
        if group_comment:
            context_instructions.append(
                "GROUP COMMENT: background context about the group of strings this one belongs to."
            )
        if entity_comment:
            context_instructions.append(
                "STRING COMMENT: authoritative translator notes (e.g. placeholders or terms to preserve) — takes precedence over stylistic choices."
            )
        if pinned_comments:
            context_instructions.append(
                "PINNED COMMENTS: high-priority guidance from the localization team's project manager."
            )
        if terms:
            context_instructions.append(
                "TERMINOLOGY: use the given translations consistently, unless incorrect for this context."
            )
        context_block = (
            "\n".join(context_instructions) + "\n\n" if context_instructions else ""
        )

        system_rules = textwrap.dedent(
            f"""\
            Rules, in priority order if they conflict:
            1) Match the English source's ending punctuation exactly (including having none), using correct target-language conventions (e.g. Spanish ¿¡, French non-breaking space before ?!:).
            2) Preserve all HTML tags and attributes exactly as in the source; translate only text content and translatable attributes (e.g. alt, title).
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
            return OpenAITranslation(text=cached, cache_hit=True)

        # Call the OpenAI API with the constructed prompt
        response = self.client.chat.completions.create(
            model=settings.OPENAI_MODEL,
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0,  # Set temperature to 0 for deterministic output
            top_p=1,  # Set top_p to 1 to consider the full distribution
            reasoning_effort="none",  # Disable reasoning for faster responses
        )

        result = response.choices[0].message.content.strip()
        set_machinery_service_cache_key(cache_key, result)
        usage = getattr(response, "usage", None)
        return OpenAITranslation(
            text=result,
            cache_hit=False,
            prompt_tokens=getattr(usage, "prompt_tokens", None),
            completion_tokens=getattr(usage, "completion_tokens", None),
        )
