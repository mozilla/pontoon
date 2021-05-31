import api from 'core/api';

import type { MachineryTranslation } from 'core/api';
import type { Locale } from 'core/locale';

export const ADD_TRANSLATIONS: 'machinery/ADD_TRANSLATIONS' =
    'machinery/ADD_TRANSLATIONS';
export const CONCORDANCE_SEARCH: 'machinery/CONCORDANCE_SEARCH' =
    'machinery/CONCORDANCE_SEARCH';
export const REQUEST: 'machinery/REQUEST' = 'machinery/REQUEST';
export const RESET: 'machinery/RESET' = 'machinery/RESET';

/**
 * Indicate that entities are currently being fetched.
 */
export type RequestAction = {
    type: typeof REQUEST;
};
export function request(): RequestAction {
    return {
        type: REQUEST,
    };
}

/**
 * Get a list of concordance search results
 */
export type ConcordanceSearchAction = {
    readonly type: typeof CONCORDANCE_SEARCH;
    readonly searchResults: Array<MachineryTranslation>;
    readonly hasMore: boolean;
};
export function concordanceSearch(
    searchResults: Array<MachineryTranslation>,
    hasMore: boolean,
): ConcordanceSearchAction {
    return {
        type: CONCORDANCE_SEARCH,
        searchResults: searchResults,
        hasMore,
    };
}

/**
 * Add a list of machine translations to the current list.
 */
export type AddTranslationsAction = {
    readonly type: typeof ADD_TRANSLATIONS;
    readonly translations: Array<MachineryTranslation>;
};
export function addTranslations(
    translations: Array<MachineryTranslation>,
): AddTranslationsAction {
    return {
        type: ADD_TRANSLATIONS,
        translations: translations,
    };
}

/**
 * Reset the list of machinery translations.
 */
export type ResetAction = {
    readonly type: typeof RESET;
    readonly entity: number | null | undefined;
    readonly sourceString: string;
};
export function reset(
    entity: number | null | undefined,
    sourceString: string,
): ResetAction {
    return {
        type: RESET,
        entity: entity,
        sourceString: sourceString,
    };
}

/**
 * Get concordance search results for a given source string and locale.
 */
export function getConcordanceSearchResults(
    source: string,
    locale: Locale,
    page?: number,
): (...args: Array<any>) => any {
    return async (dispatch) => {
        if (!page) {
            dispatch(reset(null, source));
        }

        dispatch(request());

        // Abort all previously running requests.
        await api.machinery.abort();

        api.machinery
            .getConcordanceResults(source, locale, page)
            .then((results) =>
                dispatch(concordanceSearch(results.results, results.hasMore)),
            );
    };
}

/**
 * Get all machinery results for a given source string and locale.
 *
 * This will fetch and return data from:
 *  - Translation Memory
 *  - Google Translate (if supported)
 *  - Microsoft Translator (if supported)
 *  - Systran Translate (if supported)
 *  - Microsoft Terminology (if enabled for the locale)
 *  - Caighdean (if enabled for the locale)
 */
export function get(
    source: string,
    locale: Locale,
    isAuthenticated: boolean,
    pk: number | null | undefined,
): (...args: Array<any>) => any {
    return async (dispatch) => {
        dispatch(reset(pk, source));

        // Abort all previously running requests.
        await api.machinery.abort();

        if (pk) {
            api.machinery
                .getTranslationMemory(source, locale, pk)
                .then((results) => dispatch(addTranslations(results)));
        }

        // Only make requests to paid services if user is authenticated
        if (isAuthenticated) {
            if (locale.googleTranslateCode) {
                api.machinery
                    .getGoogleTranslation(source, locale)
                    .then((results) => dispatch(addTranslations(results)));
            }

            if (locale.msTranslatorCode) {
                api.machinery
                    .getMicrosoftTranslation(source, locale)
                    .then((results) => dispatch(addTranslations(results)));
            }

            if (locale.systranTranslateCode) {
                api.machinery
                    .getSystranTranslation(source, locale)
                    .then((results) => dispatch(addTranslations(results)));
            }
        }

        if (locale.msTerminologyCode) {
            api.machinery
                .getMicrosoftTerminology(source, locale)
                .then((results) => dispatch(addTranslations(results)));
        }

        if (locale.code === 'ga-IE' && pk) {
            api.machinery
                .getCaighdeanTranslation(pk)
                .then((results) => dispatch(addTranslations(results)));
        }
    };
}

export default {
    getConcordanceSearchResults,
    addTranslations,
    get,
    reset,
};
