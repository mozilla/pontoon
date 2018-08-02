/* @flow */

import { RECEIVE, REQUEST, UPDATE } from './actions';
import type { ReceiveAction, RequestAction, UpdateAction } from './actions';


export type Action =
    | ReceiveAction
    | RequestAction
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
    +translation: Array<Translation>,
};

export type Entities = Array<DbEntity>;

// Read-only state (marked by '+').
export type State = {
    +entities: Entities,
    +fetching: boolean,
    +errors: Array<string>,
};


function updateEntities(state: Object, entity: number, translation: Translation): Entities {
    return state.entities.map(item => {
        if (item.pk !== entity) {
            return item;
        }

        return {
            ...item,
            ...{
                translation: [translation]
            },
        };
    })
}


const initial: State = {
    entities: [],
    fetching: false,
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
                ...{
                    entities: action.entities,
                    fetching: false,
                }
            };
        case REQUEST:
            return { ...state, ...{ fetching: true } };
        case UPDATE:
            return {
                ...state,
                ...{
                    entities: updateEntities(state, action.entity, action.translation),
                },
            };
        default:
            return state;
    }
}
