/* @flow */

import APIBase from './base';

export default class LocaleAPI extends APIBase {
    async get(code: string) {
        const query = `{
            locale(code: "${code}") {
                code
                name
                cldrPlurals
                pluralRule
                direction
                script
                googleTranslateCode
                msTranslatorCode
                systranTranslateCode
                msTerminologyCode
                transvision
                localizations {
                    totalStrings
                    approvedStrings
                    stringsWithWarnings
                    project {
                        slug
                        name
                    }
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
