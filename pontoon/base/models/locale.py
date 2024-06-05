import json
import logging

import requests

from django.conf import settings
from django.contrib.auth.models import Group
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import F, Prefetch

from pontoon.base.models.aggregated_stats import AggregatedStats


log = logging.getLogger(__name__)


def validate_cldr(value):
    for item in value.split(","):
        try:
            number = int(item.strip())
        except ValueError:
            return
        if number < 0 or number >= len(Locale.CLDR_PLURALS):
            raise ValidationError(
                "%s must be a list of integers between 0 and 5" % value
            )


class LocaleCodeHistory(models.Model):
    locale = models.ForeignKey("Locale", on_delete=models.CASCADE)
    old_code = models.CharField(max_length=20)
    created_at = models.DateTimeField(auto_now_add=True)


class LocaleQuerySet(models.QuerySet):
    def unsynced(self):
        """
        Filter unsynchronized locales.
        """
        return self.filter(translatedresources__isnull=True).distinct()

    def visible(self):
        """
        Visible locales have at least one TranslatedResource defined from a non
        system project.
        """
        from pontoon.base.models.project_locale import ProjectLocale

        return self.available().filter(
            pk__in=ProjectLocale.objects.visible().values_list("locale", flat=True)
        )

    def available(self):
        """
        Available locales have at least one TranslatedResource defined.
        """
        from pontoon.base.models.translated_resource import TranslatedResource

        return self.filter(
            pk__in=TranslatedResource.objects.values_list("locale", flat=True)
        )

    def prefetch_project_locale(self, project):
        """
        Prefetch ProjectLocale and latest translation data for given project.
        """
        from pontoon.base.models.project_locale import ProjectLocale

        return self.prefetch_related(
            Prefetch(
                "project_locale",
                queryset=(
                    ProjectLocale.objects.filter(project=project).prefetch_related(
                        "latest_translation__user", "latest_translation__approved_user"
                    )
                ),
                to_attr="fetched_project_locale",
            )
        )

    def get_stats_sum(self):
        """
        Get sum of stats for all items in the queryset.
        """
        return AggregatedStats.get_stats_sum(self)

    def get_top_instances(self):
        """
        Get top instances in the queryset.
        """
        return AggregatedStats.get_top_instances(self)


class Locale(AggregatedStats):
    code = models.CharField(max_length=20, unique=True)

    google_translate_code = models.CharField(
        max_length=20,
        blank=True,
        help_text="""
        Google Translate maintains its own list of
        <a href="https://translate.google.com/intl/en/about/languages/">
        supported locales</a>. Choose a matching locale from the list or leave blank to disable
        support for Google Cloud Translation machine translation service.
        """,
    )

    google_automl_model = models.CharField(
        max_length=30,
        blank=True,
        help_text="""
        ID of a custom model, trained using locale translation memory. If the value is set,
        Pontoon will use the Google AutoML Translation instead of the generic Translation API.
        """,
    )

    # Codes used by optional Microsoft services
    ms_translator_code = models.CharField(
        max_length=20,
        blank=True,
        help_text="""
        Microsoft Translator maintains its own list of
        <a href="https://docs.microsoft.com/en-us/azure/cognitive-services/translator/languages">
        supported locales</a>. Choose a matching locale from the list or leave blank to disable
        support for Microsoft Translator machine translation service.
        """,
    )
    ms_terminology_code = models.CharField(
        max_length=20,
        blank=True,
        help_text="""
        Microsoft Terminology uses language codes that include both the language and
        the country/region. Choose a matching locale from the list or leave blank to disable support
        for Microsoft terminology:

        af-za, am-et, ar-dz, ar-eg, ar-sa, as-in, az-latn-az, be-by, bg-bg, bn-bd, bn-in,
        bs-cyrl-ba, bs-latn-ba, ca-es, ca-es-valencia, chr-cher-us, cs-cz, cy-gb, da-dk, de-at,
        de-ch, de-de, el-gr, en-au, en-ca, en-gb, en-hk, en-ie, en-in, en-my, en-ng, en-nz, en-ph,
        en-pk, en-sg, en-tt, en-us, en-za, es-ar, es-bo, es-cl, es-co, es-cr, es-do, es-ec, es-es,
        es-gt, es-hn, es-mx, es-ni, es-pa, es-pe, es-pr, es-py, es-sv, es-us, es-uy, es-ve, et-ee,
        eu-es, fa-ir, fi-fi, fil-ph, fo-fo, fr-be, fr-ca, fr-ch, fr-dz, fr-fr, fr-ma, fr-tn,
        fuc-latn-sn, ga-ie, gd-gb, gl-es, gu-in, guc-ve, ha-latn-ng, he-il, hi-in, hr-hr, hu-hu,
        hy-am, id-id, ig-ng, is-is, it-ch, it-it, iu-latn-ca, ja-jp, ka-ge, kk-kz, km-kh, kn-in,
        ko-kr, kok-in, ku-arab-iq, ky-kg, lb-lu, lo-la, lt-lt, lv-lv, mi-nz, mk-mk, ml-in, mn-mn,
        mr-in, ms-bn, ms-my, mt-mt, my-mm, nb-no, ne-np, nl-be, nl-nl, nn-no, nso-za, or-in,
        pa-arab-pk, pa-in, pl-pl, prs-af, ps-af, pt-br, pt-pt, quc-latn-gt, quz-pe, ro-md, ro-ro,
        ru-kz, ru-ru, rw-rw, sd-arab-pk, si-lk, sk-sk, sl-si, sp-xl, sq-al, sr-cyrl-ba, sr-cyrl-rs,
        sr-latn-me, sr-latn-rs, sv-se, sw-ke, ta-in, te-in, tg-cyrl-tj, th-th, ti-et, tk-tm, tl-ph,
        tn-za, tr-tr, tt-ru, ug-cn, uk-ua, ur-pk, uz-cyrl-uz, uz-latn-uz, vi-vn, wo-sn, xh-za,
        yo-ng, zh-cn, zh-hk, zh-sg, zh-tw, zu-za
        """,
    )

    # Fields used by optional SYSTRAN services
    systran_translate_code = models.CharField(
        max_length=20,
        blank=True,
        help_text="""
        SYSTRAN maintains its own list of
        <a href="https://platform.systran.net/index">supported locales</a>.
        Choose a matching locale from the list or leave blank to disable
        support for SYSTRAN machine translation service.
        """,
    )
    systran_translate_profile = models.CharField(
        max_length=128,
        blank=True,
        help_text="""
        SYSTRAN Profile UUID to specify the engine trained on the en-locale language pair.
        The field is updated automatically after the systran_translate_code field changes.
        """,
    )

    db_collation = models.CharField(
        max_length=20,
        blank=True,
        help_text="""
        Some of locales require to use different database collation than default ('en_US').

        <strong>Use with caution, because it may brake the search for this locale.</strong>
        """,
    )

    name = models.CharField(max_length=128)
    plural_rule = models.CharField(
        max_length=512,
        blank=True,
        help_text="""
        Plural rule is part of the plurals header in
        <a href="https://www.gnu.org/software/gettext/manual/gettext.html#Plural-forms">
        Gettext PO files
        </a>,
        that follows the <i>plural=</i> string, without the trailing semicolon.
        E.g. (n != 1)
        """,
    )

    # Locale contains references to user groups that translate or manage them.
    # Groups store respective permissions for users.
    translators_group = models.ForeignKey(
        Group, models.SET_NULL, related_name="translated_locales", null=True
    )
    managers_group = models.ForeignKey(
        Group, models.SET_NULL, related_name="managed_locales", null=True
    )

    # CLDR Plurals
    CLDR_PLURALS = (
        (0, "zero"),
        (1, "one"),
        (2, "two"),
        (3, "few"),
        (4, "many"),
        (5, "other"),
    )

    cldr_plurals = models.CharField(
        "CLDR Plurals",
        blank=True,
        max_length=11,
        validators=[validate_cldr],
        help_text="""
        A comma separated list of
        <a href="http://www.unicode.org/cldr/charts/latest/supplemental/language_plural_rules.html">
        CLDR plural categories</a>, where 0 represents zero, 1 one, 2 two, 3 few, 4 many, and 5 other.
        E.g. 1,5
        """,
    )

    script = models.CharField(
        max_length=128,
        default="Latin",
        help_text="""
        The script used by this locale. Find it in
        <a
        href="http://www.unicode.org/cldr/charts/latest/supplemental/languages_and_scripts.html">
        CLDR Languages and Scripts</a>.
        """,
    )

    # Writing direction
    class Direction(models.TextChoices):
        LEFT_TO_RIGHT = "ltr", "left-to-right"
        RIGHT_TO_LEFT = "rtl", "right-to-left"

    direction = models.CharField(
        max_length=3,
        default=Direction.LEFT_TO_RIGHT,
        choices=Direction.choices,
        help_text="""
        Writing direction of the script. Set to "right-to-left" if "rtl" value
        for the locale script is set to "YES" in
        <a href="https://github.com/unicode-cldr/cldr-core/blob/master/scriptMetadata.json">
        CLDR scriptMetadata.json</a>.
        """,
    )

    population = models.PositiveIntegerField(
        default=0,
        help_text="""
        Number of native speakers. Find locale code in
        <a href="https://github.com/unicode-org/cldr-json/blob/main/cldr-json/cldr-core/supplemental/territoryInfo.json">CLDR territoryInfo.json</a>
        and multiply its "_populationPercent" with the territory "_population".
        Repeat if multiple occurrences of locale code exist and sum products.
        """,
    )

    team_description = models.TextField(blank=True)

    #: Most recent translation approved or created for this locale.
    latest_translation = models.ForeignKey(
        "Translation",
        models.SET_NULL,
        blank=True,
        null=True,
        related_name="locale_latest",
    )

    accesskey_localization = models.BooleanField(
        default=True,
        verbose_name="Access key localization",
        help_text="""
        Allow localization of access keys if they are part of a string.
        Some locales don't translate access keys, mostly because they use non-Latin scripts.
    """,
    )

    objects = LocaleQuerySet.as_manager()

    class Meta:
        ordering = ["name", "code"]
        permissions = (
            ("can_translate_locale", "Can add translations"),
            ("can_manage_locale", "Can manage locale"),
        )

    def __str__(self):
        return self.name

    def serialize(self):
        return {
            "code": self.code,
            "name": self.name,
            "pk": self.pk,
            "nplurals": self.nplurals,
            "plural_rule": self.plural_rule,
            "cldr_plurals": self.cldr_plurals_list_string(),
            "direction": self.direction,
            "script": self.script,
            "google_translate_code": self.google_translate_code,
            "ms_translator_code": self.ms_translator_code,
            "systran_translate_code": self.systran_translate_code,
            "ms_terminology_code": self.ms_terminology_code,
        }

    def cldr_id_list(self):
        if self.cldr_plurals == "":
            return [1]
        else:
            return [int(p) for p in self.cldr_plurals.split(",")]

    def cldr_plurals_list(self):
        return map(Locale.cldr_id_to_plural, self.cldr_id_list())

    def cldr_plurals_list_string(self):
        return ", ".join(self.cldr_plurals_list())

    @classmethod
    def cldr_plural_to_id(self, cldr_plural):
        for i in self.CLDR_PLURALS:
            if i[1] == cldr_plural:
                return i[0]

    @classmethod
    def cldr_id_to_plural(self, cldr_id):
        for i in self.CLDR_PLURALS:
            if i[0] == cldr_id:
                return i[1]

    @property
    def nplurals(self):
        return len(self.cldr_id_list())

    def available_projects_list(self, user):
        """Get a list of available project slugs."""
        return list(
            self.project_set.available()
            .visible_for(user)
            .values_list("slug", flat=True)
        ) + ["all-projects"]

    def get_plural_index(self, cldr_plural):
        """Returns plural index for given cldr name."""
        cldr_id = Locale.cldr_plural_to_id(cldr_plural)
        return self.cldr_id_list().index(cldr_id)

    def get_relative_cldr_plural(self, plural_id):
        """
        Every locale supports a subset (a list) of The CLDR Plurals forms.
        In code, we store their relative position.
        """
        return Locale.cldr_id_to_plural(self.cldr_id_list()[plural_id])

    def get_latest_activity(self, project=None):
        from pontoon.base.models.project_locale import ProjectLocale

        return ProjectLocale.get_latest_activity(self, project)

    def get_chart(self, project=None):
        from pontoon.base.models.project_locale import ProjectLocale

        return ProjectLocale.get_chart(self, project)

    def aggregate_stats(self):
        from pontoon.base.models.project import Project
        from pontoon.base.models.translated_resource import TranslatedResource

        TranslatedResource.objects.filter(
            resource__project__disabled=False,
            resource__project__system_project=False,
            resource__project__visibility=Project.Visibility.PUBLIC,
            resource__entities__obsolete=False,
            locale=self,
        ).distinct().aggregate_stats(self)

    def stats(self):
        """Get locale stats used in All Resources part."""
        return [
            {
                "title": "all-resources",
                "resource__path": [],
                "resource__total_strings": self.total_strings,
                "pretranslated_strings": self.pretranslated_strings,
                "strings_with_errors": self.strings_with_errors,
                "strings_with_warnings": self.strings_with_warnings,
                "unreviewed_strings": self.unreviewed_strings,
                "approved_strings": self.approved_strings,
            }
        ]

    def parts_stats(self, project):
        """Get locale-project paths with stats."""
        from pontoon.base.models.project_locale import ProjectLocale
        from pontoon.base.models.translated_resource import TranslatedResource

        def get_details(parts):
            return parts.order_by("title").values(
                "title",
                "resource__path",
                "resource__deadline",
                "resource__total_strings",
                "pretranslated_strings",
                "strings_with_errors",
                "strings_with_warnings",
                "unreviewed_strings",
                "approved_strings",
            )

        translatedresources = TranslatedResource.objects.filter(
            resource__project=project, resource__entities__obsolete=False, locale=self
        ).distinct()
        details = list(
            get_details(translatedresources.annotate(title=F("resource__path")))
        )

        all_resources = ProjectLocale.objects.get(project=project, locale=self)
        details.append(
            {
                "title": "all-resources",
                "resource__path": [],
                "resource__deadline": [],
                "resource__total_strings": all_resources.total_strings,
                "pretranslated_strings": all_resources.pretranslated_strings,
                "strings_with_errors": all_resources.strings_with_errors,
                "strings_with_warnings": all_resources.strings_with_warnings,
                "unreviewed_strings": all_resources.unreviewed_strings,
                "approved_strings": all_resources.approved_strings,
            }
        )

        return details

    def save(self, *args, **kwargs):
        old = Locale.objects.get(pk=self.pk) if self.pk else None
        super().save(*args, **kwargs)

        # If SYSTRAN Translate code changes, update SYSTRAN Profile UUID.
        if old is None or old.systran_translate_code == self.systran_translate_code:
            return

        if not self.systran_translate_code:
            return

        api_key = settings.SYSTRAN_TRANSLATE_API_KEY
        server = settings.SYSTRAN_TRANSLATE_SERVER
        profile_owner = settings.SYSTRAN_TRANSLATE_PROFILE_OWNER
        if not (api_key or server or profile_owner):
            return

        url = f"{server}/translation/supportedLanguages"

        payload = {
            "key": api_key,
            "source": "en",
            "target": self.systran_translate_code,
        }

        try:
            r = requests.post(url, params=payload)
            root = json.loads(r.content)

            if "error" in root:
                log.error(
                    "Unable to retrieve SYSTRAN Profile UUID: {error}".format(
                        error=root
                    )
                )
                return

            for languagePair in root["languagePairs"]:
                for profile in languagePair["profiles"]:
                    if profile["selectors"]["owner"] == profile_owner:
                        self.systran_translate_profile = profile["id"]
                        self.save(update_fields=["systran_translate_profile"])
                        return

        except requests.exceptions.RequestException as e:
            log.error(f"Unable to retrieve SYSTRAN Profile UUID: {e}")
