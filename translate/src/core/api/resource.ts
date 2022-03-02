import APIBase from './base';

export default class ResourceAPI extends APIBase {
    async getAll(locale: string, project: string): Promise<any> {
        const url = `/${locale}/${project}/parts/`;

        const headers = new Headers();
        headers.append('X-Requested-With', 'XMLHttpRequest');

        return await this.fetch(url, 'GET', null, headers);
    }
}
