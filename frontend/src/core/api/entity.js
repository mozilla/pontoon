/* @flow */

import APIBase from './base';

import type { OtherLocaleTranslation } from './types';


export default class EntityAPI extends APIBase {
    async batchEdit(
        action: string,
        locale: string,
        entities: Array<number>,
        find: ?string,
        replace: ?string,
    ) {
        const payload = new FormData();

        const csrfToken = this.getCSRFToken();
        payload.append('csrfmiddlewaretoken', csrfToken);

        payload.append('action', action);
        payload.append('locale', locale);
        payload.append('entities', entities.join(','));

        if (find) {
            payload.append('find', find);
        }

        if (replace) {
            payload.append('replace', replace);
        }

        const headers = new Headers();
        headers.append('X-Requested-With', 'XMLHttpRequest');

        return await this.fetch('/batch-edit-translations/', 'POST', payload, headers);
    }

    /**
     * Return a list of entities for a project and locale.
     *
     * Pass in a `resource` to restrict the list to a specific path.
     * If the `exclude` array has values, those entities will be excluded from
     * the query. Use this to query for the next set of entities.
     */
    async getEntities(
        locale: string,
        project: string,
        resource: string,
        entityIds: ?Array<number>,
        exclude: Array<number>,
        entity: ?string,
        search: ?string,
        status: ?string,
        extra: ?string,
        pkOnly: ?boolean,
    ): Promise<Object> {
        const payload = new FormData();
        payload.append('locale', locale);
        payload.append('project', project);

        if (resource !== 'all-resources') {
            payload.append('paths[]', resource);
        }

        if (entityIds && entityIds.length) {
            payload.append('entity_ids', entityIds.join(','));
        }

        if (exclude.length) {
            payload.append('exclude_entities', exclude.join(','));
        }

        if (entity) {
            payload.append('entity', entity);
        }

        if (search) {
            payload.append('search', search);
        }

        if (status) {
            payload.append('status', status);
        }

        if (extra) {
            payload.append('extra', extra);
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
    ) {
        const payload = new URLSearchParams();
        payload.append('entity', entity.toString());
        payload.append('locale', locale);
        payload.append('plural_form', pluralForm.toString());

        const headers = new Headers();
        headers.append('X-Requested-With', 'XMLHttpRequest');

        return await this.fetch('/get-history/', 'GET', payload, headers);
    }

    async getOtherLocales(
        entity: number,
        locale: string,
    ): Promise<Array<OtherLocaleTranslation>> {
        const payload = new URLSearchParams();
        payload.append('entity', entity.toString());
        payload.append('locale', locale);

        const headers = new Headers();
        headers.append('X-Requested-With', 'XMLHttpRequest');

        const results = await this.fetch('/other-locales/', 'GET', payload, headers);

        if (!Array.isArray(results)) {
            return [];
        }

        return results.map(entry => {
            return {
                code: entry.locale__code,
                locale: entry.locale__name,
                direction: entry.locale__direction,
                script: entry.locale__script,
                translation: entry.string,
            };
        });
    }
}
