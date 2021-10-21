import {
    CONCORDANCE_SEARCH,
    ADD_TRANSLATIONS,
    REQUEST,
    RESET,
} from './actions';

import type { MachineryTranslation } from 'core/api';
import type {
    ConcordanceSearchAction,
    AddTranslationsAction,
    RequestAction,
    ResetAction,
} from './actions';

type Action =
    | ConcordanceSearchAction
    | AddTranslationsAction
    | RequestAction
    | ResetAction;

type Translations = Array<MachineryTranslation>;

export type MachineryState = {
    entity: number | null | undefined;
    sourceString: string;
    translations: Translations;
    searchResults: Translations;
    fetching: boolean;
    hasMore?: boolean;
};

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
    const translations = oldTranslations.map((oldT) => ({ ...oldT }));

    for (const newT of newTranslations) {
        const oldT = translations.find(
            (oldT) =>
                newT.original === oldT.original &&
                newT.translation === oldT.translation,
        );
        if (!oldT) {
            translations.push({ ...newT });
        } else {
            oldT.sources.push(newT.sources[0]);
            if (newT.quality && !oldT.quality) {
                oldT.quality = newT.quality;
            }
        }
    }

    return translations.sort((a, b) => {
        if (!a.quality) return 1;
        if (!b.quality) return -1;
        if (a.quality > b.quality) return -1;
        if (a.quality < b.quality) return 1;
        return 0;
    });
}

const initial: MachineryState = {
    entity: null,
    sourceString: '',
    translations: [],
    searchResults: [],
    fetching: false,
    hasMore: false,
};

export default function reducer(
    state: MachineryState = initial,
    action: Action,
): MachineryState {
    switch (action.type) {
        case CONCORDANCE_SEARCH:
            return {
                ...state,
                searchResults: [
                    ...state.searchResults,
                    ...action.searchResults,
                ],
                fetching: false,
                hasMore: action.hasMore,
            };
        case ADD_TRANSLATIONS:
            return {
                ...state,
                translations: dedupedTranslations(
                    state.translations,
                    action.translations,
                ),
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
                searchResults: [],
                hasMore: false,
            };
        default:
            return state;
    }
}
