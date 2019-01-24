/* @flow */

import api from 'core/api';

import type { Locale } from 'core/locales';
import type { DbEntity } from 'modules/entitieslist';


export const ADD_TRANSLATIONS: 'machinery/ADD_TRANSLATIONS' = 'machinery/ADD_TRANSLATIONS';
export const RESET: 'machinery/RESET' = 'machinery/RESET';


/**
 * Add a list of machine translations to the current list.
 */
export type AddTranslationsAction = {
    +type: typeof ADD_TRANSLATIONS,
    +translations: Array<api.types.MachineryTranslation>,
};
export function addTranslations(
    translations: Array<api.types.MachineryTranslation>
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
};
export function reset(): ResetAction {
    return {
        type: RESET,
    };
}


/**
 * Get all machinery results for a given entity.
 *
 * This will fetch and return data from:
 *  - Translation Memory
 *  - Google Translate (if supported)
 *  - Microsoft Translator (if supported)
 *  - Microsoft Terminology (if enabled for the locale)
 *  - Transvision (if enabled for the locale)
 *  - Caighdean (if enabled for the locale)
 */
export function get(entity: DbEntity, locale: Locale): Function {
    return async dispatch => {
        dispatch(reset());

        const memory = await api.machinery.getTranslationMemory(entity, locale);
        dispatch(addTranslations(memory));

        const googleTranslation = await api.machinery.getGoogleTranslation(entity, locale);
        dispatch(addTranslations(googleTranslation));

        const microsoftTranslation = await api.machinery.getMicrosoftTranslation(entity, locale);
        dispatch(addTranslations(microsoftTranslation));

        if (locale.msTerminologyCode) {
            const msTerminology = await api.machinery.getMicrosoftTerminology(entity, locale);
            dispatch(addTranslations(msTerminology));
        }

        if (locale.transvision) {
            const transvisionMemory = await api.machinery.getTransvisionMemory(entity, locale);
            dispatch(addTranslations(transvisionMemory));
        }

        if (locale.code === 'ga-IE') {
            const caighdean = await api.machinery.getCaighdeanTranslation(entity, locale);
            dispatch(addTranslations(caighdean));
        }
    }
}


export default {
    addTranslations,
    get,
    reset,
};
