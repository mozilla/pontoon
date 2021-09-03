# Generated manually on 2021-09-03 10:07

from django.db import migrations


_activity_sql = """
WITH filt AS (
  WITH
    sync AS (SELECT id FROM auth_user WHERE email = 'pontoon-sync@example.com')
  SELECT
    act.created_at::date AS created_at,
    tra.locale_id,
    res.project_id,
    action_type = 'translation:created' AND cardinality(tra.machinery_sources) = 0 AS human_translation,
    action_type = 'translation:created' AND cardinality(tra.machinery_sources) != 0 AS machinery_translation,
    act.performed_by_id = sync.id AS is_sync,
    act.action_type = 'translation:created' AND (tra.approved_date IS NULL OR tra.approved_date > tra.date) AS new_suggestion,
    (
      (action_type = 'translation:approved' AND act.performed_by_id = tra.user_id) OR
      (action_type = 'translation:created' AND act.performed_by_id = tra.approved_user_id)
    ) AS self_approved,
    action_type = 'translation:approved' AND act.performed_by_id != tra.user_id AS peer_approved,
    action_type = 'translation:rejected' AS rejected
  FROM
    sync,
    actionlog_actionlog AS act,
    base_translation AS tra,
    base_entity AS ent,
    base_resource AS res
  WHERE
    act.translation_id = tra.id AND
    tra.entity_id = ent.id AND
    ent.resource_id = res.id
), sums AS (
  SELECT
    created_at,
    project_id,
    count(*) FILTER (WHERE filt.human_translation) AS human_translations,
    count(*) FILTER (WHERE filt.machinery_translation) AS machinery_translations,
    count(*) FILTER (WHERE NOT is_sync AND filt.new_suggestion) AS new_suggestions,
    count(*) FILTER (WHERE NOT is_sync AND filt.self_approved) AS self_approved,
    count(*) FILTER (WHERE NOT is_sync AND filt.peer_approved) AS peer_approved,
    count(*) FILTER (WHERE NOT is_sync AND filt.rejected) AS rejected
  FROM insights_projectinsightssnapshot JOIN filt USING (created_at, project_id)
  GROUP BY created_at, project_id
)
UPDATE insights_projectinsightssnapshot AS ins
SET
  human_translations = sums.human_translations,
  machinery_translations = sums.machinery_translations,
  new_suggestions = sums.new_suggestions,
  self_approved = sums.self_approved,
  peer_approved = sums.peer_approved,
  rejected = sums.rejected
FROM sums
WHERE
  ins.created_at = sums.created_at + 1 AND
  ins.project_id = sums.project_id;
"""

_reverse_activity_sql = """
UPDATE insights_projectinsightssnapshot
SET
  human_translations = 0,
  machinery_translations = 0,
  new_suggestions = 0,
  self_approved = 0,
  peer_approved = 0,
  rejected = 0;
"""

_new_sources_sql = """
WITH ents AS (
  SELECT ent.date_created::date AS created_at, project_id, count(*)
  FROM
    base_entity AS ent,
    base_resource AS res,
    base_project AS proj
  WHERE
    ent.resource_id = res.id AND
    res.project_id = proj.id AND
    NOT proj.disabled AND
    NOT proj.system_project AND
    proj.visibility = 'public'
  GROUP BY ent.date_created::date, project_id
)
UPDATE insights_projectinsightssnapshot AS ins
SET new_source_strings = ents.count
FROM ents
WHERE
  ins.created_at = ents.created_at + 1 AND
  ins.project_id = ents.project_id;
"""

_reverse_new_sources_sql = """
UPDATE insights_projectinsightssnapshot SET new_source_strings = 0;
"""


class Migration(migrations.Migration):

    dependencies = [
        ("insights", "0003_project_insights"),
    ]

    operations = [
        migrations.RunSQL(sql=_activity_sql, reverse_sql=_reverse_activity_sql),
        migrations.RunSQL(sql=_new_sources_sql, reverse_sql=_reverse_new_sources_sql),
    ]
