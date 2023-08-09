# Generated by Django 3.2.4 on 2021-11-30 19:56

import statistics

from datetime import datetime, timedelta
from django.db import migrations
from django.db.models import F
from sacrebleu.metrics import CHRF


chrfpp = CHRF(word_order=2)


def populate_pretranslation_quality(apps, schema_editor):
    ActionLog = apps.get_model("actionlog", "ActionLog")
    LocaleInsightsSnapshot = apps.get_model("insights", "LocaleInsightsSnapshot")
    ProjectLocaleInsightsSnapshot = apps.get_model(
        "insights", "ProjectLocaleInsightsSnapshot"
    )
    Translation = apps.get_model("base", "Translation")

    def get_chrf_score(action):
        try:
            approved_translation = Translation.objects.get(
                entity=action["translation__entity"],
                locale=action["translation__locale"],
                approved=True,
            ).string
        except Translation.DoesNotExist:
            return

        score = chrfpp.sentence_score(
            action["translation__string"], [approved_translation]
        )
        return float(score.format(score_only=True))

    def store_data(key, action_data, action):
        if key not in action_data:
            action_data[key] = {
                "pretranslations_chrf_score": list(),
                "pretranslations_approved": set(),
                "pretranslations_rejected": set(),
                "pretranslations_new": set(),
            }

        data = action_data[key]
        translation = action["translation"]

        if action["action_type"] == "translation:created":
            data["pretranslations_new"].add(translation)

        elif action["action_type"] == "translation:approved":
            data["pretranslations_approved"].add(translation)
            # Translation has been approved, no need to claculate the chrF++ score
            data["pretranslations_chrf_score"].append(100)

        elif action["action_type"] == "translation:rejected":
            data["pretranslations_rejected"].add(translation)
            score = get_chrf_score(action)
            if score:
                data["pretranslations_chrf_score"].append(score)

    def update_snapshots(Model, action_data):
        changed_snapshots = []

        # Update snapshots
        for key, value in action_data.items():
            try:
                if len(key) == 2:
                    locale, created_at = key
                    snapshot = Model.objects.get(locale=locale, created_at=created_at)
                elif len(key) == 3:
                    project, locale, created_at = key
                    snapshot = Model.objects.get(
                        project_locale__project=project,
                        project_locale__locale=locale,
                        created_at=created_at,
                    )
            except Model.DoesNotExist:
                continue

            scores = [i for i in value["pretranslations_chrf_score"] if i != 0]
            snapshot.pretranslations_chrf_score = (
                statistics.mean(scores) if scores else 0
            )
            snapshot.pretranslations_approved = len(value["pretranslations_approved"])
            snapshot.pretranslations_rejected = len(value["pretranslations_rejected"])
            snapshot.pretranslations_new = len(value["pretranslations_new"])

            changed_snapshots.append(snapshot)

        Model.objects.bulk_update(
            changed_snapshots,
            [
                "pretranslations_chrf_score",
                "pretranslations_new",
                "pretranslations_approved",
                "pretranslations_rejected",
            ],
            batch_size=1000,
        )

    actions = (
        ActionLog.objects.filter(
            translation__entity__resource__project__system_project=False,
            translation__entity__resource__project__visibility="public",
            translation__user__email__in=[
                "pontoon-tm@example.com",
                "pontoon-mt@example.com",
            ],
            action_type__in=[
                "translation:created",
                "translation:approved",
                "translation:rejected",
            ],
        )
        .exclude(performed_by__email="pontoon-sync@example.com")
        .values(
            "created_at",
            "action_type",
            "translation",
            "translation__entity",
            "translation__locale",
            "translation__string",
            project=F("translation__entity__resource__project"),
        )
    )

    # Store action data in a dict for faster matching with snapshots
    locale_action_data = dict()
    project_locale_action_data = dict()

    for action in actions:
        locale_key = (action["translation__locale"], action["created_at"].date())
        store_data(locale_key, locale_action_data, action)

        project_locale_key = (
            action["project"],
            action["translation__locale"],
            action["created_at"].date(),
        )
        store_data(project_locale_key, project_locale_action_data, action)

    update_snapshots(LocaleInsightsSnapshot, locale_action_data)
    update_snapshots(ProjectLocaleInsightsSnapshot, project_locale_action_data)


def reset_pretranslation_quality(apps, schema_editor):
    LocaleInsightsSnapshot = apps.get_model("insights", "LocaleInsightsSnapshot")
    ProjectLocaleInsightsSnapshot = apps.get_model(
        "insights", "ProjectLocaleInsightsSnapshot"
    )

    LocaleInsightsSnapshot.objects.exclude(
        pretranslations_chrf_score=0,
        pretranslations_approved=0,
        pretranslations_rejected=0,
        pretranslations_new=0,
    ).update(
        pretranslations_chrf_score=0,
        pretranslations_approved=0,
        pretranslations_rejected=0,
        pretranslations_new=0,
    )

    ProjectLocaleInsightsSnapshot.objects.exclude(
        pretranslations_chrf_score=0,
        pretranslations_approved=0,
        pretranslations_rejected=0,
        pretranslations_new=0,
    ).update(
        pretranslations_chrf_score=0,
        pretranslations_approved=0,
        pretranslations_rejected=0,
        pretranslations_new=0,
    )


class Migration(migrations.Migration):

    dependencies = [
        ("insights", "0013_pretranslation_quality"),
    ]

    operations = [
        migrations.RunPython(
            code=populate_pretranslation_quality,
            reverse_code=reset_pretranslation_quality,
        ),
    ]
