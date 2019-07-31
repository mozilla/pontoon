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
    +lastCheckedEntity: ?number,
    +requestInProgress: ?string,
    +response: ?ResponseType,
|};


const initial: BatchActionsState = {
    entities: [],
    lastCheckedEntity: null,
    requestInProgress: null,
    response: null,
};


function checkEntities(
    state_entities: Array<number>,
    action_entities: Array<number>,
) {
    // Union with duplicates removed
    return state_entities.concat(
        action_entities.filter(
            e => state_entities.indexOf(e) < 0
        )
    );
}


function toggleEntity(
    entities: Array<number>,
    entity: number,
) {
    // Remove entity if present
    if (entities.includes(entity)) {
        return entities.filter(e => e !== entity);
    }
    // Add entity if not present
    else {
        return entities.concat([entity]);
    }
}


function uncheckEntities(
    state_entities: Array<number>,
    action_entities: Array<number>,
) {
    return state_entities.filter(e => action_entities.indexOf(e) < 0);
}


export default function reducer(
    state: BatchActionsState = initial,
    action: Action,
): BatchActionsState {
    switch (action.type) {
        case CHECK:
            return {
                ...state,
                entities: checkEntities(state.entities, action.entities),
                lastCheckedEntity: action.lastCheckedEntity,
            };
        case RECEIVE:
            return {
                ...state,
                requestInProgress: null,
                response: action.response,
            };
        case REQUEST:
            return {
                ...state,
                requestInProgress: action.source,
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
                entities: uncheckEntities(state.entities, action.entities),
                lastCheckedEntity: action.lastCheckedEntity,
            };
        default:
            return state;
    }
}
