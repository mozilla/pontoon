/* @flow */

import APIBase from './base';


export default class LocaleAPI extends APIBase {
    async getAll() {
        const query = `{
            locales {
                code
                name
                cldrPlurals
                pluralRule
                direction
            }
        }`;
        const payload = new URLSearchParams();
        payload.append('query', query);

        const headers = new Headers();
        headers.append('X-Requested-With', 'XMLHttpRequest');

        return await this.fetch('/graphql/', 'GET', payload, headers);
    }
}
