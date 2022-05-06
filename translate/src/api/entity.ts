import { LocationType } from '~/context/location';

import { GET, POST } from './_base';
import { getCSRFToken } from './_csrfToken';
import { keysToCamelCase } from './_keysToCamelCase';
import type {
  APIStats,
  EntityTranslation,
  HistoryTranslation,
} from './translation';

/**
 * String that needs to be translated, along with its current metadata,
 * and its currently accepted translations.
 */
export type Entity = {
  readonly pk: number;
  readonly original: string;
  readonly original_plural: string;
  readonly machinery_original: string;
  readonly comment: string;
  readonly group_comment: string;
  readonly resource_comment: string;
  readonly key: string;
  readonly context: string;
  readonly format: string;
  readonly path: string;
  readonly project: Record<string, any>;
  readonly source: Array<Array<string>> | Record<string, any>;
  readonly translation: Array<EntityTranslation>;
  readonly readonly: boolean;
  readonly isSibling: boolean;
};

/**
 * Lists of preceding and succeeding entities
 */
export type EntitySiblings = {
  readonly preceding: Array<Entity>;
  readonly succeeding: Array<Entity>;
};

type BatchEditResponse =
  | { count: number; invalid_translation_count?: number }
  | { error: true };

export async function batchEditEntities(
  action: string,
  locale: string,
  entityIds: number[],
  find: string | undefined,
  replace: string | undefined,
): Promise<BatchEditResponse> {
  const csrfToken = getCSRFToken();
  const payload = new FormData();
  payload.append('csrfmiddlewaretoken', csrfToken);
  payload.append('action', action);
  payload.append('locale', locale);
  payload.append('entities', entityIds.join(','));
  if (find) {
    payload.append('find', find);
  }
  if (replace) {
    payload.append('replace', replace);
  }

  return await POST('/batch-edit-translations/', payload);
}

type EntitiesResponse =
  | { entities: Entity[]; has_next: boolean; stats: APIStats }
  | { entities?: never; has_next: false; stats: {} };

/**
 * Return a list of entities for a project and locale.
 *
 * Pass in a `resource` to restrict the list to a specific path.
 * If the `exclude` array has values, those entities will be excluded from
 * the query. Use this to query for the next set of entities.
 */
export async function fetchEntities(
  location: LocationType,
  exclude: Entity[],
): Promise<EntitiesResponse> {
  const payload = buildFetchPayload(location);
  if (exclude.length > 0) {
    payload.append('exclude_entities', exclude.map((ent) => ent.pk).join(','));
  }
  return await POST('/get-entities/', payload);
}

export async function fetchEntitiesById(
  { locale, project, resource }: LocationType,
  entityIds: number[],
): Promise<{ entities: Entity[]; stats: APIStats }> {
  const payload = buildFetchPayload({ locale, project, resource });
  payload.append('entity_ids', entityIds.join(','));
  return await POST('/get-entities/', payload);
}

export async function fetchEntityIds(
  location: LocationType,
): Promise<number[]> {
  const payload = buildFetchPayload(location);
  payload.append('pk_only', 'true');
  const { entity_pks } = await POST('/get-entities/', payload);
  return Array.isArray(entity_pks) ? entity_pks : [];
}

function buildFetchPayload(
  location: Pick<LocationType, 'locale' | 'project' | 'resource'> &
    Partial<LocationType>,
): FormData {
  const { locale, project, resource, entity } = location;

  const payload = new FormData();
  payload.append('locale', locale);
  payload.append('project', project);
  if (resource !== 'all-resources') {
    payload.append('paths[]', resource);
  }
  if (entity) {
    payload.append('entity', String(entity));
  }

  for (const key of [
    'search',
    'status',
    'extra',
    'tag',
    'author',
    'time',
  ] as const) {
    const value = location[key];
    if (value) {
      payload.append(key, value);
    }
  }

  return payload;
}

export async function fetchSiblingEntities(
  entity: number,
  locale: string,
): Promise<EntitySiblings> {
  const search = new URLSearchParams({ entity: String(entity), locale });
  const results = await GET('/get-sibling-entities/', search);
  return keysToCamelCase(results);
}

export async function fetchEntityHistory(
  entity: number,
  locale: string,
  pluralForm: number = -1,
): Promise<HistoryTranslation[]> {
  const search = new URLSearchParams({
    entity: String(entity),
    locale,
    plural_form: String(pluralForm),
  });
  const results = await GET('/get-history/', search, { singleton: true });
  return Array.isArray(results) ? keysToCamelCase(results) : [];
}
