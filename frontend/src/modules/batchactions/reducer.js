/* @flow */

import { RESET, TOGGLE } from './actions';

import type { ResetAction, ToggleAction } from './actions';


type Action =
    | ResetAction
    | ToggleAction
;

export type BatchActionsState = {|
    +entities: Array<number>,
|};


const initial: BatchActionsState = {
    entities: [],
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
        case TOGGLE:
            return {
                ...state,
                entities: toggleEntity(state.entities, action.entity),
            };
        case RESET:
            return {
                ...initial,
            };
        default:
            return state;
    }
}
