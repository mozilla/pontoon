/* @flow */

import { ADD_TRANSLATIONS, REQUEST, RESET } from './actions';

import type { MachineryTranslation } from 'core/api';
import type {
    AddTranslationsAction,
    RequestAction,
    ResetAction,
} from './actions';

type Action = AddTranslationsAction | RequestAction | ResetAction;

type Translations = Array<MachineryTranslation>;

export type MachineryState = {|
    entity: ?number,
    sourceString: string,
    translations: Translations,
    fetching: boolean,
    hasMore?: boolean,
|};

/**
 * Return a list of translations that are deduplicated and sorted.
 *
 * The deduplication process works as follow:
 * If a new translation has the same `original` and `translation` than
 * an existing one, then add that translation's `source` to the previous one.
 * Otherwise, add the translation to the list.
 *
 * Translations are sorted by descending quality (highest quality comes first).
 */
function dedupedTranslations(
    oldTranslations: Translations,
    newTranslations: Translations,
): Translations {
    const translations = oldTranslations.map((item) => ({ ...item }));

    newTranslations.forEach((newT) => {
        const sameTranslation = translations.findIndex(
            (oldT) =>
                newT.original === oldT.original &&
                newT.translation === oldT.translation,
        );

        if (sameTranslation >= 0) {
            translations[sameTranslation].sources.push(newT.sources[0]);

            if (newT.quality && !translations[sameTranslation].quality) {
                translations[sameTranslation].quality = newT.quality;
            }

            if (
                newT.projectNames &&
                !translations[sameTranslation].projectNames
            ) {
                translations[sameTranslation].projectNames = newT.projectNames;
            }
        } else {
            translations.push({ ...newT });
        }
    });

    return translations.sort((a, b) => {
        if (!a.quality && !b.quality) {
            return 1;
        }
        if (!a.quality && b.quality) {
            return 1;
        }
        if (a.quality && !b.quality) {
            return -1;
        }
        if (a.quality && b.quality) {
            if (a.quality > b.quality) {
                return -1;
            }
            if (a.quality < b.quality) {
                return 1;
            }
        }
        return 0;
    });
}

const initial: MachineryState = {
    entity: null,
    sourceString: '',
    translations: [],
    fetching: false,
    hasMore: false,
};

export default function reducer(
    state: MachineryState = initial,
    action: Action,
): MachineryState {
    switch (action.type) {
        case ADD_TRANSLATIONS:
            return {
                ...state,
                translations: dedupedTranslations(
                    state.translations,
                    action.translations,
                ),
                fetching: false,
                hasMore: action.hasMore,
            };
        case REQUEST:
            return {
                ...state,
                fetching: true,
                hasMore: false,
            };
        case RESET:
            return {
                ...state,
                entity: action.entity,
                sourceString: action.sourceString,
                translations: [],
            };
        default:
            return state;
    }
}
