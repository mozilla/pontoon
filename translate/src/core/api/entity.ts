import { LocationType } from '~/context/location';
import APIBase from './base';

import type { OtherLocaleTranslations } from './types';

export default class EntityAPI extends APIBase {
  async batchEdit(
    action: string,
    locale: string,
    entityIds: number[],
    find: string | undefined,
    replace: string | undefined,
  ): Promise<any> {
    const payload = new FormData();

    const csrfToken = this.getCSRFToken();
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

    const headers = new Headers();
    headers.append('X-Requested-With', 'XMLHttpRequest');

    return await this.fetch(
      '/batch-edit-translations/',
      'POST',
      payload,
      headers,
    );
  }

  /**
   * Return a list of entities for a project and locale.
   *
   * Pass in a `resource` to restrict the list to a specific path.
   * If the `exclude` array has values, those entities will be excluded from
   * the query. Use this to query for the next set of entities.
   */
  async getEntities(
    location: Pick<LocationType, 'locale' | 'project' | 'resource'> &
      Partial<LocationType>,
    {
      entity,
      entityIds = [],
      exclude = [],
      pkOnly = false,
    }: {
      entity?: number;
      entityIds?: number[];
      exclude?: number[];
      pkOnly?: boolean;
    },
  ): Promise<Record<string, any>> {
    const { locale, project, resource } = location;

    const payload = new FormData();
    payload.append('locale', locale);
    payload.append('project', project);

    if (resource !== 'all-resources') {
      payload.append('paths[]', resource);
    }

    if (entityIds.length > 0) {
      payload.append('entity_ids', entityIds.join(','));
    }

    if (exclude.length) {
      payload.append('exclude_entities', exclude.join(','));
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

    if (pkOnly) {
      payload.append('pk_only', 'true');
    }

    const headers = new Headers();
    headers.append('X-Requested-With', 'XMLHttpRequest');

    return await this.fetch('/get-entities/', 'POST', payload, headers);
  }

  async getHistory(
    entity: number,
    locale: string,
    pluralForm: number = -1,
  ): Promise<unknown[]> {
    const payload = new URLSearchParams();
    payload.append('entity', entity.toString());
    payload.append('locale', locale);
    payload.append('plural_form', pluralForm.toString());

    const headers = new Headers();
    headers.append('X-Requested-With', 'XMLHttpRequest');

    const results = await this.fetch('/get-history/', 'GET', payload, headers);

    // On error or abort, fetch() returns an empty object
    return Array.isArray(results) ? this.keysToCamelCase(results) : [];
  }

  async getSiblingEntities(entity: number, locale: string): Promise<any> {
    const payload = new URLSearchParams();
    payload.append('entity', entity.toString());
    payload.append('locale', locale);
    const headers = new Headers();
    headers.append('X-Requested-With', 'XMLHttpRequest');

    const results = await this.fetch(
      '/get-sibling-entities/',
      'GET',
      payload,
      headers,
    );

    return this.keysToCamelCase(results);
  }

  async getOtherLocales(
    entity: number,
    locale: string,
  ): Promise<OtherLocaleTranslations> {
    const payload = new URLSearchParams();
    payload.append('entity', entity.toString());
    payload.append('locale', locale);

    const headers = new Headers();
    headers.append('X-Requested-With', 'XMLHttpRequest');

    const results = await this.fetch(
      '/other-locales/',
      'GET',
      payload,
      headers,
    );

    if (results.status === false) {
      return [];
    }

    return results as OtherLocaleTranslations;
  }

  async getTeamComments(entity: number, locale: string): Promise<any> {
    const payload = new URLSearchParams();
    payload.append('entity', entity.toString());
    payload.append('locale', locale);

    const headers = new Headers();
    headers.append('X-Requested-With', 'XMLHttpRequest');

    const results = await this.fetch(
      '/get-team-comments/',
      'GET',
      payload,
      headers,
    );

    return this.keysToCamelCase(results);
  }

  async getTerms(sourceString: string, locale: string): Promise<any> {
    const payload = new URLSearchParams();
    payload.append('source_string', sourceString);
    payload.append('locale', locale);

    const headers = new Headers();
    headers.append('X-Requested-With', 'XMLHttpRequest');

    const results = await this.fetch(
      '/terminology/get-terms/',
      'GET',
      payload,
      headers,
    );

    return this.keysToCamelCase(results);
  }
}
