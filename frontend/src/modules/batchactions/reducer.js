/* @flow */

import {
    CHECK,
    RECEIVE,
    REQUEST,
    RESET,
    RESET_RESPONSE,
    TOGGLE,
    UNCHECK
} from './actions';

import type {
    CheckAction,
    ReceiveAction,
    RequestAction,
    ResetAction,
    ResetResponseAction,
    ResponseType,
    ToggleAction,
    UncheckAction
} from './actions';


type Action =
    | CheckAction
    | ReceiveAction
    | RequestAction
    | ResetAction
    | ResetResponseAction
    | ToggleAction
    | UncheckAction
;

export type BatchActionsState = {|
    +entities: Array<number>,
    +fetching: ?string,
    +lastCheckedEntity: ?number,
    +response: ?ResponseType,
|};


const initial: BatchActionsState = {
    entities: [],
    fetching: null,
    lastCheckedEntity: null,
    response: null,
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
        case RECEIVE:
            return {
                ...state,
                fetching: null,
                response: action.response,
            };
        case REQUEST:
            return {
                ...state,
                fetching: action.source,
            };
        case RESET:
            return {
                ...initial,
            };
        case RESET_RESPONSE:
            return {
                ...state,
                response: initial.response,
            };
        case TOGGLE:
            return {
                ...state,
                entities: toggleEntity(state.entities, action.entity),
                lastCheckedEntity: action.entity,
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
