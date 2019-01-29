/* @flow */

import APIBase from './base';

import type { Locale } from 'core/locales';
import type { DbEntity } from 'modules/entitieslist';
import type { MachineryTranslation } from './types';


type Translations = Array<MachineryTranslation>;


export default class MachineryAPI extends APIBase {
    async _get(url: string, params: Object) {
        const payload = new URLSearchParams();
        for (let param in params) {
            payload.append(param, params[param]);
        }

        const headers = new Headers();
        headers.append('X-Requested-With', 'XMLHttpRequest');

        return await this.fetch(url, 'GET', payload, headers);
    }

    /**
     * Return translations from Pontoon's memory.
     */
    async getTranslationMemory(entity: DbEntity, locale: Locale): Promise<Translations> {
        const url = '/translation-memory/';
        const params = {
            text: entity.original,
            locale: locale.code,
            pk: entity.pk,
        };

        const results = await this._get(url, params);

        return results.map(item => {
            return {
                source: 'Translation memory',
                url: '/',
                title: 'Pontoon Homepage',
                original: item.source,
                translation: item.target,
                quality: Math.round(item.quality) + '%',
                count: item.count,
            };
        });
    }

    /**
     * Return translation by Google Translate.
     */
    async getGoogleTranslation(entity: DbEntity, locale: Locale): Promise<Translations> {
        const url = '/google-translate/';
        const params = {
            text: entity.original,
            locale: locale.googleTranslateCode,
        };

        const result = await this._get(url, params);

        if (result.translation) {
            return [{
                source: 'Google Translate',
                url: 'https://translate.google.com/',
                title: 'Visit Google Translate',
                original: entity.original,
                translation: result.translation,
            }];
        }

        return [];
    }

    /**
     * Return translation by Microsoft Translator.
     */
    async getMicrosoftTranslation(entity: DbEntity, locale: Locale): Promise<Translations> {
        const url = '/microsoft-translator/';
        const params = {
            text: entity.original,
            locale: locale.msTranslatorCode,
        };

        const result = await this._get(url, params);

        if (result.translation) {
            return [{
                source: 'Microsoft Translator',
                url: 'https://www.bing.com/translator',
                title: 'Visit Bing Translator',
                original: entity.original,
                translation: result.translation,
            }];
        }

        return [];
    }

    /**
     * Return translations from Microsoft Terminology.
     */
    async getMicrosoftTerminology(entity: DbEntity, locale: Locale): Promise<Translations> {
        const url = '/microsoft-terminology/';
        const params = {
            text: entity.original,
            locale: locale.msTerminologyCode,
        };

        const results = await this._get(url, params);

        return results.map(item => {
            return {
                source: 'Microsoft',
                url: 'https://www.microsoft.com/Language/en-US/Search.aspx?sString=' +
                     item.source + '&langID=' + locale.msTerminologyCode,
                title: 'Visit Microsoft Terminology Service API.\n' +
                       '© 2018 Microsoft Corporation. All rights reserved.',
                original: item.source,
                translation: item.target,
                quality: Math.round(item.quality) + '%',
            };
        });
    }

    /**
     * Return translations from Transvision.
     */
    async getTransvisionMemory(entity: DbEntity, locale: Locale): Promise<Translations> {
        const url = '/transvision/';
        const params = {
            text: entity.original,
            locale: locale.code,
        };

        const results = await this._get(url, params);

        return results.map(item => {
            return {
                source: 'Mozilla',
                url: 'https://transvision.mozfr.org/?repo=global' +
                     '&recherche=' + encodeURIComponent(entity.original) +
                     '&locale=' + locale.code,
                title: 'Visit Transvision',
                original: item.source,
                translation: item.target,
                quality: Math.round(item.quality) + '%',
            };
        });
    }

    /**
     * Return translation by Caighdean Machine Translation.
     *
     * Works only for the `ga-IE` locale.
     */
    async getCaighdeanTranslation(entity: DbEntity, locale: Locale): Promise<Translations> {
        const url = '/caighdean/';
        const params = {
            id: entity.pk,
            locale: locale.code,
        };

        const result = await this._get(url, params);

        if (result.translation) {
            return [{
                source: 'Caighdean',
                url: 'https://github.com/kscanne/caighdean',
                title: 'Visit Caighdean Machine Translation',
                original: result.original,
                translation: result.translation,
            }];
        }

        return [];
    }
}
