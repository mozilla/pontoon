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


function updateEntities(state: Object, entity: number, translation: Translation): Entities {
    return state.entities.map(item => {
        if (item.pk !== entity) {
            return item;
        }

        return {
            ...item,
            translation: [translation]
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
                entities: updateEntities(state, action.entity, action.translation),
            };
        default:
            return state;
    }
}
