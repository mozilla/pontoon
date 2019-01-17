/* @flow */

import APIBase from './base';


const SETTINGS_NAMES_MAP = {
    'runQualityChecks': 'quality_checks',
    'forceSuggestions': 'force_suggestions',
};


export default class UserAPI extends APIBase {
    /**
     * Return a list of entities for a project and locale.
     *
     * Pass in a `resource` to restrict the list to a specific path.
     * If the `exclude` array has values, those entities will be excluded from
     * the query. Use this to query for the next set of entities.
     */
    async get(): Promise<Object> {
        const headers = new Headers();
        headers.append('X-Requested-With', 'XMLHttpRequest');

        return await this.fetch('/user-data/', 'GET', null, headers);
    }

    async updateSetting(username: string, setting: string, value: boolean): Promise<string> {
        const csrfToken = this.getCSRFToken();

        const payload = new URLSearchParams();
        payload.append('attribute', SETTINGS_NAMES_MAP[setting]);
        payload.append('value', value.toString());
        payload.append('csrfmiddlewaretoken', csrfToken);

        const headers = new Headers();
        headers.append('X-Requested-With', 'XMLHttpRequest');
        headers.append('X-CSRFToken', csrfToken);

        return await this.fetch(`/api/v1/user/${username}/`, 'POST', payload, headers);
    }
}
