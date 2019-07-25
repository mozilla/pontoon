/* @flow */

import { CHECK, RESET, SELECT_ALL, TOGGLE, UNCHECK } from './actions';

import type { CheckAction, ResetAction, SelectAllAction, ToggleAction, UncheckAction } from './actions';


type Action =
    | CheckAction
    | ResetAction
    | SelectAllAction
    | ToggleAction
    | UncheckAction
;

export type BatchActionsState = {|
    +entities: Array<number>,
    +lastCheckedEntity: number | null,
|};


const initial: BatchActionsState = {
    entities: [],
    lastCheckedEntity: null,
};


function toggleEntity(entities: Array<number>, entity: number) {
    // Remove entity if present
    if (entities.includes(entity)) {
        return entities.filter(e => e !== entity);
    }
    // Add entity if not present
    else {
        return entities.concat([entity]);
    }
}


export default function reducer(
    state: BatchActionsState = initial,
    action: Action,
): BatchActionsState {
    switch (action.type) {
        case CHECK:
            return {
                ...state,
                // Union with duplicates removed
                entities: state.entities.concat(
                    action.entities.filter(
                        e => state.entities.indexOf(e) < 0
                    )
                ),
                lastCheckedEntity: action.lastCheckedEntity,
            };
        case TOGGLE:
            return {
                ...state,
                entities: toggleEntity(state.entities, action.entity),
                lastCheckedEntity: action.entity,
            };
        case RESET:
            return {
                ...initial,
            };
        case SELECT_ALL:
            return {
                entities: action.entities,
                lastCheckedEntity: action.lastCheckedEntity,
            };
        case UNCHECK:
            return {
                ...state,
                entities: state.entities.filter(e => action.entities.indexOf(e) < 0),
                lastCheckedEntity: action.lastCheckedEntity,
            };
        default:
            return state;
    }
}
