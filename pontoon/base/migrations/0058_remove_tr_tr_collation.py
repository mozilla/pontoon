# Generated manually on 2024-04-04

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("base", "0057_remove_lang_format"),
    ]

    operations = [
        migrations.RunSQL(
            sql="UPDATE base_locale SET db_collation='tr-x-icu' WHERE db_collation='tr_tr';",
        ),
        migrations.RunSQL(
            sql="DROP COLLATION IF EXISTS tr_tr;",
            reverse_sql="CREATE COLLATION tr_tr (LOCALE = 'tr_TR.utf8');",
        ),
    ]
