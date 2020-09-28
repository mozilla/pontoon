/* @flow */

import APIBase from './base';

export default class FilterAPI extends APIBase {
    /**
     * Return data needed for filtering strings.
     */
    async get(locale: string, project: string, resource: string) {
        const headers = new Headers();
        headers.append('X-Requested-With', 'XMLHttpRequest');

        return await this.fetch(
            `/${locale}/${project}/${resource}/authors-and-time-range/`,
            'GET',
            null,
            headers,
        );
    }
}
