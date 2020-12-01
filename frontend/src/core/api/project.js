/* @flow */

import APIBase from './base';

export default class ProjectAPI extends APIBase {
    async get(slug: string) {
        const query = `{
            project(slug: "${slug}") {
                slug
                name
                info
                tags {
                    name
                    slug
                    priority
                }
            }
        }`;

        const payload = new URLSearchParams();
        payload.append('query', query);

        const headers = new Headers();
        headers.append('X-Requested-With', 'XMLHttpRequest');

        return await this.fetch('/graphql', 'GET', payload, headers);
    }
}
