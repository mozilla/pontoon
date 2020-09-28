/* @flow */

import api from 'core/api';

import type { MachineryTranslation } from 'core/api';
import type { Locale } from 'core/locale';

export const ADD_TRANSLATIONS: 'machinery/ADD_TRANSLATIONS' =
    'machinery/ADD_TRANSLATIONS';
export const RESET: 'machinery/RESET' = 'machinery/RESET';

/**
 * Add a list of machine translations to the current list.
 */
export type AddTranslationsAction = {
    +type: typeof ADD_TRANSLATIONS,
    +translations: Array<MachineryTranslation>,
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
 *  - Microsoft Terminology (if enabled for the locale)
 *  - Transvision (if enabled for the locale)
 *  - Caighdean (if enabled for the locale)
 */
export function get(source: string, locale: Locale, pk: ?number): Function {
    return async (dispatch) => {
        dispatch(reset(pk, source));

        // Abort all previously running requests.
        await api.machinery.abort();

        api.machinery
            .getTranslationMemory(source, locale, pk)
            .then((results) => dispatch(addTranslations(results)));

        api.machinery
            .getGoogleTranslation(source, locale)
            .then((results) => dispatch(addTranslations(results)));

        api.machinery
            .getMicrosoftTranslation(source, locale)
            .then((results) => dispatch(addTranslations(results)));

        if (locale.systranTranslateCode) {
            api.machinery
                .getSystranTranslation(source, locale)
                .then((results) => dispatch(addTranslations(results)));
        }

        if (locale.msTerminologyCode) {
            api.machinery
                .getMicrosoftTerminology(source, locale)
                .then((results) => dispatch(addTranslations(results)));
        }

        if (locale.transvision) {
            api.machinery
                .getTransvisionMemory(source, locale)
                .then((results) => dispatch(addTranslations(results)));
        }

        if (locale.code === 'ga-IE' && pk) {
            api.machinery
                .getCaighdeanTranslation(source, locale, pk)
                .then((results) => dispatch(addTranslations(results)));
        }
    };
}

export default {
    addTranslations,
    get,
    reset,
};
