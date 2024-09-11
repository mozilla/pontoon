import { Location } from '~/context/Location';

import { GET, POST } from './utils/base';
import { getCSRFToken } from './utils/csrfToken';
import { keysToCamelCase } from './utils/keysToCamelCase';
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
  readonly date_created: string;
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
  action: 'approve' | 'reject' | 'replace',
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
  | { entities: Entity[]; has_next?: boolean; stats: APIStats }
  | { entities?: never; has_next: false; stats: {} };

/**
 * Return a list of entities for a project and locale.
 *
 * Pass in a `resource` to restrict the list to a specific path.
 */
export async function fetchEntities(
  location: Location & { list: number[] },
): Promise<{ entities: Entity[]; stats: APIStats }>;
export async function fetchEntities(
  location: Location,
  page: number,
): Promise<EntitiesResponse>;
export async function fetchEntities(
  location: Location,
  page?: number,
): Promise<EntitiesResponse> {
  const payload = buildFetchPayload(location);
  if (page) {
    payload.append('page', String(page));
  }
  return await POST('/get-entities/', payload);
}

export async function fetchEntityIds(location: Location): Promise<number[]> {
  const payload = buildFetchPayload(location);
  payload.append('pk_only', 'true');
  const { entity_pks } = await POST('/get-entities/', payload);
  return Array.isArray(entity_pks) ? entity_pks : [];
}

function buildFetchPayload(
  location: Pick<Location, 'locale' | 'project' | 'resource'> &
    Partial<Location>,
): FormData {
  const { locale, project, resource, entity, list } = location;

  const payload = new FormData();
  payload.append('locale', locale);
  payload.append('project', project);
  if (resource !== 'all-resources') {
    payload.append('paths[]', resource);
  }

  if (list) {
    payload.append('entity_ids', list.join(','));
  } else {
    if (entity) {
      payload.append('entity', String(entity));
    }
    for (const key of [
      'search',
      'status',
      'search_identifiers',
      'search_translations_only',
      'search_rejected_translations',
      'search_match_case',
      'search_match_whole_word',
      'extra',
      'tag',
      'author',
      'time',
      'reviewer',
      'review_time',
      'exclude_self_reviewed',
    ] as const) {
      const value = location[key];
      if (value) {
        payload.append(key, String(value));
      }
    }
  }

  return payload;
}

export async function fetchSiblingEntities(
  entity: number,
  locale: string,
): Promise<EntitySiblings> {
  const search = new URLSearchParams({ entity: String(entity), locale });
  return GET('/get-sibling-entities/', search);
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
