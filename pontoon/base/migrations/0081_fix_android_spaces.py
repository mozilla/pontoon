from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ("base", "0080_project_date_modified"),
    ]

    operations = [
        migrations.RunSQL(
            r"""
WITH tm AS (
    SELECT
        t.id,
        regexp_replace(trim(BOTH FROM m.target), '\s\s+', ' ', 'g') AS string
    FROM base_translationmemoryentry m
    JOIN base_translation t ON t.id = m.translation_id
    WHERE
        m.target SIMILAR TO '%[^\S \n]%' AND
        t.string != m.target
)
UPDATE base_translation AS t
SET string = tm.string
FROM tm
WHERE t.id = tm.id AND
    t.string = regexp_replace(tm.string, '[^\S \n]', ' ', 'g');
"""
        ),
    ]
