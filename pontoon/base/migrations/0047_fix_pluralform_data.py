# Generated manually on 2023-10-10

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0046_projectslughistory"),
    ]

    operations = [
        migrations.RunSQL(sql="""
UPDATE base_translation AS tx
SET plural_form = 0
FROM base_entity AS ent
WHERE
  tx.plural_form IS NULL AND
  tx.entity_id = ent.id AND
  ent.string_plural != '';
"""),
    ]
