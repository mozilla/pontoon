/* @flow */

import {
    CHECK,
    RECEIVE,
    REQUEST,
    RESET,
    RESET_RESPONSE,
    TOGGLE,
    UNCHECK,
} from './actions';

import type {
    CheckAction,
    ReceiveAction,
    RequestAction,
    ResetAction,
    ResetResponseAction,
    ResponseType,
    ToggleAction,
    UncheckAction,
} from './actions';

type Action =
    | CheckAction
    | ReceiveAction
    | RequestAction
    | ResetAction
    | ResetResponseAction
    | ToggleAction
    | UncheckAction;

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
    stateEntities: Array<number>,
    actionEntities: Array<number>,
) {
    // Union with duplicates removed
    return stateEntities.concat(
        actionEntities.filter((e) => stateEntities.indexOf(e) < 0),
    );
}

function toggleEntity(entities: Array<number>, entity: number) {
    // Remove entity if present
    if (entities.includes(entity)) {
        return entities.filter((e) => e !== entity);
    }
    // Add entity if not present
    else {
        return entities.concat([entity]);
    }
}

function uncheckEntities(
    stateEntities: Array<number>,
    actionEntities: Array<number>,
) {
    return stateEntities.filter((e) => actionEntities.indexOf(e) < 0);
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
