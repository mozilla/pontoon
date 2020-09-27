/* @flow */

import APIBase from './base';

import type { Locale } from 'core/locale';
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
    async getTranslationMemory(
        source: string,
        locale: Locale,
        pk: ?number,
    ): Promise<Translations> {
        const url = '/translation-memory/';
        const params = {
            text: source,
            locale: locale.code,
            pk: (pk || '').toString(),
        };

        const results = await this._get(url, params);

        if (!Array.isArray(results)) {
            return [];
        }

        return results.map((item): MachineryTranslation => {
            return {
                sources: ['translation-memory'],
                itemCount: item.count,
                original: item.source,
                translation: item.target,
                quality: Math.round(item.quality),
            };
        });
    }

    /**
     * Return translation by Google Translate.
     */
    async getGoogleTranslation(
        source: string,
        locale: Locale,
    ): Promise<Translations> {
        const url = '/google-translate/';
        const params = {
            text: source,
            locale: locale.googleTranslateCode,
        };

        const result = await this._get(url, params);

        if (!result.translation) {
            return [];
        }

        return [
            {
                sources: ['google-translate'],
                original: source,
                translation: result.translation,
            },
        ];
    }

    /**
     * Return translation by Microsoft Translator.
     */
    async getMicrosoftTranslation(
        source: string,
        locale: Locale,
    ): Promise<Translations> {
        const url = '/microsoft-translator/';
        const params = {
            text: source,
            locale: locale.msTranslatorCode,
        };

        const result = await this._get(url, params);

        if (!result.translation) {
            return [];
        }

        return [
            {
                sources: ['microsoft-translator'],
                original: source,
                translation: result.translation,
            },
        ];
    }

    /**
     * Return translations by SYSTRAN.
     */
    async getSystranTranslation(
        source: string,
        locale: Locale,
    ): Promise<Translations> {
        const url = '/systran-translate/';
        const params = {
            text: source,
            locale: locale.systranTranslateCode,
        };

        const result = await this._get(url, params);

        if (!result.translation) {
            return [];
        }

        return [
            {
                sources: ['systran-translate'],
                original: source,
                translation: result.translation,
            },
        ];
    }

    /**
     * Return translations from Microsoft Terminology.
     */
    async getMicrosoftTerminology(
        source: string,
        locale: Locale,
    ): Promise<Translations> {
        const url = '/microsoft-terminology/';
        const params = {
            text: source,
            locale: locale.msTerminologyCode,
        };

        const results = await this._get(url, params);

        if (!results.translations) {
            return [];
        }

        return results.translations.map((item): MachineryTranslation => {
            return {
                sources: ['microsoft-terminology'],
                original: item.source,
                translation: item.target,
                quality: Math.round(item.quality),
            };
        });
    }

    /**
     * Return translations from Transvision.
     */
    async getTransvisionMemory(
        source: string,
        locale: Locale,
    ): Promise<Translations> {
        const url = '/transvision/';
        const params = {
            text: source,
            locale: locale.code,
        };

        const results = await this._get(url, params);

        return results.map((item): MachineryTranslation => {
            return {
                sources: ['transvision'],
                original: item.source,
                translation: item.target,
                quality: Math.round(item.quality),
            };
        });
    }

    /**
     * Return translation by Caighdean Machine Translation.
     *
     * Works only for the `ga-IE` locale.
     */
    async getCaighdeanTranslation(
        source: string,
        locale: Locale,
        pk: number,
    ): Promise<Translations> {
        const url = '/caighdean/';
        const params = {
            id: pk,
            locale: locale.code,
        };

        const result = await this._get(url, params);

        if (!result.translation) {
            return [];
        }

        return [
            {
                sources: ['caighdean'],
                original: result.original,
                translation: result.translation,
            },
        ];
    }
}
