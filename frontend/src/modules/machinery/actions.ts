import api from 'core/api';

import type { MachineryTranslation } from 'core/api';
import type { Locale } from 'core/locale';
import type { AppThunk } from 'store';

export const ADD_TRANSLATIONS = 'machinery/ADD_TRANSLATIONS';
export const CONCORDANCE_SEARCH = 'machinery/CONCORDANCE_SEARCH';
export const REQUEST = 'machinery/REQUEST';
export const RESET_SEARCH = 'machinery/RESET_SEARCH';
export const SET_ENTITY = 'machinery/SET_ENTITY';

/**
 * Indicate that entities are currently being fetched.
 */
export type RequestAction = {
    type: typeof REQUEST;
};
export const request = (): RequestAction => ({ type: REQUEST });

/**
 * Get a list of concordance search results
 */
export type ConcordanceSearchAction = {
    readonly type: typeof CONCORDANCE_SEARCH;
    readonly searchResults: Array<MachineryTranslation>;
    readonly hasMore: boolean;
};
export const concordanceSearch = (
    searchResults: Array<MachineryTranslation>,
    hasMore: boolean,
): ConcordanceSearchAction => ({
    type: CONCORDANCE_SEARCH,
    searchResults: searchResults,
    hasMore,
});

/**
 * Add a list of machine translations to the current list.
 */
export type AddTranslationsAction = {
    readonly type: typeof ADD_TRANSLATIONS;
    readonly translations: Array<MachineryTranslation>;
};
export const addTranslations = (
    translations: Array<MachineryTranslation>,
): AddTranslationsAction => ({
    type: ADD_TRANSLATIONS,
    translations: translations,
});

/**
 * Reset the list of machinery translations for a new search.
 */
export type ResetSearchAction = {
    readonly type: typeof RESET_SEARCH;
    readonly searchString: string;
};
export const resetSearch = (searchString: string): ResetSearchAction => ({
    type: RESET_SEARCH,
    searchString,
});

/**
 * Set the current entity.
 */
export type SetEntityAction = {
    readonly type: typeof SET_ENTITY;
    readonly entity: number | null | undefined;
    readonly sourceString: string;
};
export const setEntity = (
    entity: number | null | undefined,
    sourceString: string,
): SetEntityAction => ({
    type: SET_ENTITY,
    entity: entity,
    sourceString: sourceString,
});

/**
 * Get concordance search results for a given source string and locale.
 */
export const getConcordanceSearchResults = (
    source: string,
    locale: Locale,
    page?: number,
): AppThunk => async (dispatch) => {
    dispatch(request());

    // Abort all previously running requests.
    await api.machinery.abort();

    const { results, hasMore } = await api.machinery.getConcordanceResults(
        source,
        locale,
        page,
    );
    dispatch(concordanceSearch(results, hasMore));
};

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
export const get = (
    source: string,
    locale: Locale,
    isAuthenticated: boolean,
    pk: number | null | undefined,
): AppThunk => async (dispatch) => {
    // Abort all previously running requests.
    await api.machinery.abort();

    if (pk) {
        const results = await api.machinery.getTranslationMemory(
            source,
            locale,
            pk,
        );
        dispatch(addTranslations(results));
    }

    // Only make requests to paid services if user is authenticated
    if (isAuthenticated) {
        if (locale.googleTranslateCode) {
            const results = await api.machinery.getGoogleTranslation(
                source,
                locale,
            );
            dispatch(addTranslations(results));
        }

        if (locale.msTranslatorCode) {
            const results = await api.machinery.getMicrosoftTranslation(
                source,
                locale,
            );
            dispatch(addTranslations(results));
        }

        if (locale.systranTranslateCode) {
            const results = await api.machinery.getSystranTranslation(
                source,
                locale,
            );
            dispatch(addTranslations(results));
        }
    }

    if (locale.msTerminologyCode) {
        const results = await api.machinery.getMicrosoftTerminology(
            source,
            locale,
        );
        dispatch(addTranslations(results));
    }

    if (locale.code === 'ga-IE' && pk) {
        const results = await api.machinery.getCaighdeanTranslation(pk);
        dispatch(addTranslations(results));
    }
};

export default {
    getConcordanceSearchResults,
    addTranslations,
    get,
    resetSearch,
    setEntity,
};
