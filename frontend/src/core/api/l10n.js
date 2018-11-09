/* @flow */

import APIBase from './base';


export default class L10nAPI extends APIBase {
    /**
     * Return a string with translations for a given locale.
     */
    async get(locale: string) {
        const url = this.getFullURL(`/static/locale/${locale}/translate.ftl`);
        const response = await fetch(url);
        return await response.text();
    }

    /**
     * Return the preferred locale of the current user.
     */
    async getPreferredLocales(): Promise<Array<string>> {
        const headers = new Headers();
        headers.append('X-Requested-With', 'XMLHttpRequest');

        const result = await this.fetch('/user-preferred-locale/', 'GET', null, headers);

        const locales = [ result.locale ];
        if (result.locale !== 'en-US') {
            locales.push('en-US');
        }
        return locales;
    }
}
