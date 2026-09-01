import logging

from django.db import migrations


log = logging.getLogger(__name__)

# Apostrophe-like characters seen in the data, e.g. Ge'ez / Geʻez / Geʼez / Geʽez.
APOSTROPHES = "\u2018\u2019\u02bb\u02bc\u02bd\u0060\u00b4"


def normalize_key(value):
    """Lowercase, collapse whitespace and unify apostrophes, for lookup."""
    value = " ".join(value.split()).lower()
    for char in APOSTROPHES:
        value = value.replace(char, "'")
    return value


# Every free-text value observed in the `script` field in production,
# mapped to its ISO 15924 code. Keys are matched through normalize_key().
SCRIPT_MAP = {
    "arab": "Arab",
    "arabic": "Arab",
    "armenian": "Armn",
    "bengali": "Beng",
    "cyrillic": "Cyrl",
    "cyrl": "Cyrl",
    "deva": "Deva",
    "devanagari": "Deva",
    "ethiopic": "Ethi",
    "ge'ez": "Ethi",
    "georgian": "Geor",
    "greek": "Grek",
    "gujarati": "Gujr",
    "gurmukhi": "Guru",
    "gurmukhī": "Guru",
    "hans": "Hans",
    "hant": "Hant",
    "hebrew": "Hebr",
    "japanese": "Jpan",
    "kannada": "Knda",
    "khmer": "Khmr",
    "knda": "Knda",
    "korean": "Kore",
    "lao": "Laoo",
    "latin": "Latn",
    "malayalam": "Mlym",
    "meetei mayek": "Mtei",
    "myanmar": "Mymr",
    "mymr": "Mymr",
    "nkoo": "Nkoo",
    "odia": "Orya",
    "ol chiki": "Olck",
    "simplified chinese": "Hans",
    "sinhalese": "Sinh",
    "syrc": "Syrc",
    "tamil": "Taml",
    "telugu": "Telu",
    "tfng": "Tfng",
    "thaana": "Thaa",
    "thai": "Thai",
    "tibetan": "Tibt",
    "tibt": "Tibt",
    "traditional chinese": "Hant",
}


def normalize_script(apps, schema_editor):
    Locale = apps.get_model("base", "Locale")
    for locale in Locale.objects.exclude(script="").iterator():
        script = SCRIPT_MAP.get(normalize_key(locale.script))
        if script is None:
            log.warning(
                f"Locale {locale.code}: cannot map script {locale.script!r} "
                f"to an ISO 15924 code, clearing it"
            )
            script = ""
        if script != locale.script:
            locale.script = script
            locale.save(update_fields=["script"])


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0131_fix_gettext_plural_catchall"),
    ]

    operations = [
        migrations.RunPython(
            code=normalize_script,
            reverse_code=migrations.RunPython.noop,
            elidable=False,
        ),
    ]
