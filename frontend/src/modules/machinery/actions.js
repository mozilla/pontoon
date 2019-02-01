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

        api.machinery.getTranslationMemory(entity, locale)
        .then(results => dispatch(addTranslations(results)));

        api.machinery.getGoogleTranslation(entity, locale)
        .then(results => dispatch(addTranslations(results)));

        api.machinery.getMicrosoftTranslation(entity, locale)
        .then(results => dispatch(addTranslations(results)));

        if (locale.msTerminologyCode) {
            api.machinery.getMicrosoftTerminology(entity, locale)
            .then(results => dispatch(addTranslations(results)));
        }

        if (locale.transvision) {
            api.machinery.getTransvisionMemory(entity, locale)
            .then(results => dispatch(addTranslations(results)));
        }

        if (locale.code === 'ga-IE') {
            api.machinery.getCaighdeanTranslation(entity, locale)
            .then(results => dispatch(addTranslations(results)));
        }
    }
}


export default {
    addTranslations,
    get,
    reset,
};
