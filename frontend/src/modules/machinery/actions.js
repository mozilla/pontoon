/* @flow */

import api from 'core/api';

import type { MachineryTranslation } from 'core/api';
import type { Locale } from 'core/locale';

export const ADD_TRANSLATIONS: 'machinery/ADD_TRANSLATIONS' =
    'machinery/ADD_TRANSLATIONS';
export const REQUEST: 'machinery/REQUEST' = 'machinery/REQUEST';
export const RESET: 'machinery/RESET' = 'machinery/RESET';

/**
 * Indicate that entities are currently being fetched.
 */
export type RequestAction = {
    type: typeof REQUEST,
};
export function request(): RequestAction {
    return {
        type: REQUEST,
    };
}

/**
 * Add a list of machine translations to the current list.
 */
export type AddTranslationsAction = {
    +type: typeof ADD_TRANSLATIONS,
    +translations: Array<MachineryTranslation>,
    +hasMore?: boolean,
};
export function addTranslations(
    translations: Array<MachineryTranslation>,
    hasMore?: boolean,
): AddTranslationsAction {
    return {
        type: ADD_TRANSLATIONS,
        translations: translations,
        hasMore,
    };
}

/**
 * Reset the list of machinery translations.
 */
export type ResetAction = {
    +type: typeof RESET,
    +entity: ?number,
    +sourceString: string,
};
export function reset(entity: ?number, sourceString: string): ResetAction {
    return {
        type: RESET,
        entity: entity,
        sourceString: sourceString,
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
    pk: ?number,
    page?: number,
): Function {
    return async (dispatch) => {
        if (!page) {
            dispatch(reset(pk, source));
        }

        dispatch(request());

        // Abort all previously running requests.
        await api.machinery.abort();

        if (!pk) {
            api.machinery
                .getConcordanceResults(source, locale, page)
                .then((results) =>
                    dispatch(addTranslations(results.results, results.hasMore)),
                );
        } else {
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
    addTranslations,
    get,
    reset,
};
