/* @flow */

import { RECEIVE, REQUEST, RESET, UPDATE } from './actions';
import type { ReceiveAction, RequestAction, ResetAction, UpdateAction } from './actions';


export type Action =
    | ReceiveAction
    | RequestAction
    | ResetAction
    | UpdateAction
;

export type Translation = {
    +string: ?string,
    +approved: boolean,
    +fuzzy: boolean,
    +rejected: boolean,
};

export type DbEntity = {
    +pk: number,
    +original: string,
    +original_plural: string,
    +comment: string,
    +key: string,
    +format: string,
    +path: string,
    +project: Object,
    +source: Array<Array<string>> | Object,
    +translation: Array<Translation>,
};

export type Entities = Array<DbEntity>;

// Read-only state (marked by '+').
export type State = {
    +entities: Entities,
    +fetching: boolean,
    +hasMore: boolean,
    +errors: Array<string>,
};


function updateEntityTranslation(
    state: Object,
    entity: number,
    pluralForm: number,
    translation: Translation
): Entities {
    return state.entities.map(item => {
        if (item.pk !== entity) {
            return item;
        }

        const translations = [ ...item.translation ];

        // If the plural form is -1, then there's no plural and we should
        // simply update the first translation.
        const plural = pluralForm === -1 ? 0 : pluralForm;
        translations[plural] = translation;

        return {
            ...item,
            translation: translations,
        };
    })
}


const initial: State = {
    entities: [],
    fetching: false,
    hasMore: true,
    errors: [],
};

export default function reducer(
    state: State = initial,
    action: Action,
): State {
    switch (action.type) {
        case RECEIVE:
            return {
                ...state,
                entities: state.entities.concat(action.entities),
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
                    action.translation
                ),
            };
        default:
            return state;
    }
}
