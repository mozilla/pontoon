/* @flow */

import APIBase from './base';

export default class L10nAPI extends APIBase {
    async get(locale: string) {
        const url = this.getFullURL(`/static/locale/${locale}/translate.ftl`);
        const response = await fetch(url);
        return await response.text();
    }
}
