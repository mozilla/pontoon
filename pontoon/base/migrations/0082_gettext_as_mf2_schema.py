from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0081_gettext_as_mf2_data"),
    ]
    operations = [
        migrations.RemoveConstraint(
            model_name="translation", name="entity_locale_plural_form_active"
        ),
        migrations.RemoveConstraint(
            model_name="translation", name="entity_locale_active"
        ),
        migrations.RemoveIndex(
            model_name="entity", name="base_entity_resourc_f99fa1_idx"
        ),
        migrations.RemoveField(model_name="entity", name="string_plural"),
        migrations.RemoveField(model_name="translation", name="plural_form"),
        migrations.AddIndex(
            model_name="entity",
            index=models.Index(
                fields=["resource", "obsolete"], name="base_entity_resourc_16f82b_idx"
            ),
        ),
        migrations.AddConstraint(
            model_name="translation",
            constraint=models.UniqueConstraint(
                condition=models.Q(("active", True)),
                fields=("entity", "locale", "active"),
                name="entity_locale_active",
            ),
        ),
    ]
