import { RECEIVE, REQUEST, RESET, UPDATE, RECEIVE_SIBLINGS } from './actions';

import type { Entities, EntityTranslation, EntitySiblings } from 'core/api';
import type {
    ReceiveAction,
    RequestAction,
    ResetAction,
    UpdateAction,
    ReceiveSiblingsAction,
} from './actions';

export type Action =
    | ReceiveAction
    | RequestAction
    | ResetAction
    | UpdateAction
    | ReceiveSiblingsAction;

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

function injectSiblingEntities(
    entities: Entities,
    siblings: EntitySiblings,
    entity: number,
): Entities {
    const index = entities.findIndex((item) => item.pk === entity);
    let parentEntity = entities[index];
    const currentPKs = entities.map((e) => e.pk);
    let newEntitiesState = entities.slice();

    // filtering out parent entities already present in the list
    const precedingSiblings = siblings.preceding.filter(
        (sibling) => !currentPKs.includes(sibling.pk),
    );

    const succeedingSiblings = siblings.succeeding.filter(
        (sibling) => !currentPKs.includes(sibling.pk),
    );

    let list = [...precedingSiblings, parentEntity, ...succeedingSiblings];

    newEntitiesState.splice(index, 1, ...list);

    // This block removes duplicated siblings
    newEntitiesState = newEntitiesState.filter(
        (currentValue, index, array) =>
            array.findIndex((e) => e.pk === currentValue.pk) === index,
    );
    return newEntitiesState;
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
        case RECEIVE_SIBLINGS:
            return {
                ...state,
                entities: injectSiblingEntities(
                    state.entities,
                    action.siblings,
                    action.entity,
                ),
            };
        default:
            return state;
    }
}
