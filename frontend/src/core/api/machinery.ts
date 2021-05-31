import APIBase from './base';

import type { Locale } from 'core/locale';
import type { MachineryTranslation } from './types';

type Translations = Array<MachineryTranslation>;

type ConcordanceTranslations = {
    results: Array<MachineryTranslation>;
    hasMore: boolean;
};

export default class MachineryAPI extends APIBase {
    async _get(url: string, params: Record<string, any>): Promise<any> {
        const payload = new URLSearchParams();
        for (let param in params) {
            payload.append(param, params[param]);
        }

        const headers = new Headers();
        headers.append('X-Requested-With', 'XMLHttpRequest');

        return await this.fetch(url, 'GET', payload, headers);
    }

    /**
     * Return results from Concordance search.
     */
    async getConcordanceResults(
        source: string,
        locale: Locale,
        page?: number,
    ): Promise<ConcordanceTranslations> {
        const url = '/concordance-search/';
        const params = {
            text: source,
            locale: locale.code,
            page: (page || 1).toString(),
        };

        const results = await this._get(url, params);

        if (!results.results || !Array.isArray(results.results)) {
            return { results: [], hasMore: false };
        }

        const searchResults = results.results.map(
            (item): MachineryTranslation => {
                return {
                    sources: ['concordance-search'],
                    original: item.source,
                    translation: item.target,
                    projectNames: item.project_names,
                };
            },
        );

        return { results: searchResults, hasMore: results.has_next };
    }

    /**
     * Return translations from Pontoon's memory.
     */
    async getTranslationMemory(
        source: string,
        locale: Locale,
        pk: number | null | undefined,
    ): Promise<Translations> {
        const url = '/translation-memory/';
        let params = {
            text: source,
            locale: locale.code,
        };

        if (pk) {
            params[pk] = pk;
        }

        const results = await this._get(url, params);

        if (!Array.isArray(results)) {
            return [];
        }

        return results.map(
            (item): MachineryTranslation => {
                return {
                    sources: ['translation-memory'],
                    itemCount: item.count,
                    original: item.source,
                    translation: item.target,
                    quality: Math.round(item.quality),
                };
            },
        );
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

        return results.translations.map(
            (item): MachineryTranslation => {
                return {
                    sources: ['microsoft-terminology'],
                    original: item.source,
                    translation: item.target,
                };
            },
        );
    }

    /**
     * Return translation by Caighdean Machine Translation.
     *
     * Works only for the `ga-IE` locale.
     */
    async getCaighdeanTranslation(pk: number): Promise<Translations> {
        const url = '/caighdean/';
        const params = {
            id: pk,
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
