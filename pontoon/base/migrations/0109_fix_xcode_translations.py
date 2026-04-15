from moz.l10n.formats.mf2 import mf2_parse_message, mf2_serialize_message
from moz.l10n.formats.xliff import xliff_parse_message, xliff_serialize_message

from django.db import migrations
from django.utils import timezone


def is_fixed(translation):
    db_str = translation.string
    db_msg = mf2_parse_message(db_str)
    xcode_str = xliff_serialize_message(db_msg)
    fixed_msg = xliff_parse_message(xcode_str, is_xcode=True)
    fixed_str = mf2_serialize_message(fixed_msg)
    if fixed_str != db_str:
        translation.string = fixed_str
        return True
    return False


def fix_xcode_translations(apps, schema_editor):
    Translation = apps.get_model("base", "Translation")

    translations = Translation.objects.filter(
        entity__resource__format="xcode", entity__string__contains="arg1"
    )
    trans_fixed = [t for t in translations if is_fixed(t)]

    now = timezone.now()
    trans_dupe_ids = []
    for pt in Translation.objects.filter(entity__in={t.entity for t in trans_fixed}):
        ft = next(
            (
                t
                for t in trans_fixed
                if t.entity_id == pt.entity_id
                and t.locale_id == pt.locale_id
                and t.string == pt.string
            ),
            None,
        )
        if ft is not None:
            if pt.active:
                ft.active = True
            if pt.approved:
                ft.approved = True
                ft.approved_date = min(
                    t
                    for t in (ft.approved_date, pt.approved_date, now, now)
                    if t is not None
                )
                ft.rejected = False
            trans_dupe_ids.append(pt.id)

    n, _ = Translation.objects.filter(id__in=trans_dupe_ids).delete()
    print(f" (deleted {n} duplicate Xcode translations)", end="", flush=True)
    n = Translation.objects.bulk_update(
        trans_fixed,
        ["string", "active", "approved", "approved_date", "rejected"],
    )
    print(f" (fixed {n} Xcode translations)", end="", flush=True)


class Migration(migrations.Migration):
    dependencies = [("base", "0108_delete_socialapps")]
    operations = [
        migrations.RunPython(
            fix_xcode_translations, reverse_code=migrations.RunPython.noop
        ),
    ]
