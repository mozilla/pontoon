import { RECEIVE, REQUEST, RESET, UPDATE } from './actions';

import type { Entities, EntityTranslation } from 'core/api';
import type {
    ReceiveAction,
    RequestAction,
    ResetAction,
    UpdateAction,
} from './actions';

export type Action = ReceiveAction | RequestAction | ResetAction | UpdateAction;

// Read-only state.
export type EntitiesState = {
    readonly entities: Entities;
    readonly fetching: boolean;
    readonly fetchCount: number;
    readonly hasMore: boolean;
};

function updateEntityTranslation(
    state: EntitiesState,
    entity: number,
    pluralForm: number,
    translation: EntityTranslation,
): Entities {
    return state.entities.map((item) => {
        if (item.pk !== entity) {
            return item;
        }

        const translations = [...item.translation];

        // If the plural form is -1, then there's no plural and we should
        // simply update the first translation.
        const plural = pluralForm === -1 ? 0 : pluralForm;
        translations[plural] = translation;

        return {
            ...item,
            translation: translations,
        };
    });
}

const initial: EntitiesState = {
    entities: [],
    fetching: false,
    fetchCount: 0,
    hasMore: true,
};

export default function reducer(
    state: EntitiesState = initial,
    action: Action,
): EntitiesState {
    switch (action.type) {
        case RECEIVE:
            return {
                ...state,
                entities: [...state.entities, ...action.entities],
                fetching: false,
                fetchCount: state.fetchCount + 1,
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
                entities: [],
                fetching: false,
                hasMore: true,
            };
        case UPDATE:
            return {
                ...state,
                entities: updateEntityTranslation(
                    state,
                    action.entity,
                    action.pluralForm,
                    action.translation,
                ),
            };
        default:
            return state;
    }
}
