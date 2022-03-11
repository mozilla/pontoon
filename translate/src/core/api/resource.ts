import APIBase from './base';

type APIResource = {
  readonly title: string;
  readonly approved_strings: number;
  readonly strings_with_warnings: number;
  readonly resource__total_strings: number;
};

export default class ResourceAPI extends APIBase {
  async getAll(locale: string, project: string): Promise<APIResource[]> {
    const url = `/${locale}/${project}/parts/`;

    const headers = new Headers();
    headers.append('X-Requested-With', 'XMLHttpRequest');

    return await this.fetch(url, 'GET', null, headers);
  }
}
