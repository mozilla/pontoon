/* @flow */

import api from 'core/api';


export const CHECK: 'batchactions/CHECK' = 'batchactions/CHECK';
export const RECEIVE: 'batchactions/RECEIVE' = 'batchactions/RECEIVE';
export const REQUEST: 'batchactions/REQUEST' = 'batchactions/REQUEST';
export const RESET: 'batchactions/RESET' = 'batchactions/RESET';
export const RESET_RESPONSE: 'batchactions/RESET_RESPONSE' = 'batchactions/RESET_RESPONSE';
export const TOGGLE: 'batchactions/TOGGLE' = 'batchactions/TOGGLE';
export const UNCHECK: 'batchactions/UNCHECK' = 'batchactions/UNCHECK';


export type CheckAction = {|
    type: typeof CHECK,
    entities: Array<number>,
    lastCheckedEntity: number,
|};
export function checkSelection(
    entities: Array<number>,
    lastCheckedEntity: number,
): CheckAction {
    return {
        type: CHECK,
        entities,
        lastCheckedEntity,
    };
}


export function performAction(
    action: string,
    locale: string,
    entities: Array<number>,
    find: ?string,
    replace: ?string,
): Function {
    return async dispatch => {
        dispatch(request(action));

        const data = await api.entity.batchEdit(
            action,
            locale,
            entities,
            find,
            replace,
        );

        const response = {};
        response.action = action;

        if ('count' in data) {
            response.changedCount = data.count;
            response.invalidCount = data.invalid_translation_count;
        }
        else {
            response.error = true;
        }

        dispatch(receive(response));

        setTimeout(() => {
            dispatch(reset_response());
        }, 3000);
    };
}


export type ResponseType = {
    action: string,
    changedCount: ?number,
    invalidCount: ?number,
    error: ?boolean,
};

export type ReceiveAction = {|
    response: ?ResponseType,
    type: typeof RECEIVE,
|};
export function receive(response: ?ResponseType): ReceiveAction {
    return {
        response,
        type: RECEIVE,
    };
}


export type RequestAction = {|
    source: string,
    type: typeof REQUEST,
|};
export function request(source: string): RequestAction {
    return {
        source,
        type: REQUEST,
    };
}


export type ResetResponseAction = {|
    type: typeof RESET_RESPONSE,
|};
export function reset_response(): ResetResponseAction {
    return {
        type: RESET_RESPONSE,
    };
}


export type ResetAction = {|
    type: typeof RESET,
|};
export function resetSelection(): ResetAction {
    return {
        type: RESET,
    };
}


export function selectAll(
    locale: string,
    project: string,
    resource: string,
    search: ?string,
    status: ?string,
): Function {
    return async dispatch => {
        dispatch(request('select-all'));

        const content = await api.entity.getEntities(
            locale,
            project,
            resource,
            [],
            null,
            search,
            status,
            true,
        );

        const entities = content.entity_pks;

        dispatch(receive());
        dispatch(checkSelection(entities, entities[0]));
    };
}


export type ToggleAction = {|
    type: typeof TOGGLE,
    entity: number,
|};
export function toggleSelection(entity: number): ToggleAction {
    return {
        type: TOGGLE,
        entity,
    };
}


export type UncheckAction = {|
    type: typeof UNCHECK,
    entities: Array<number>,
    lastCheckedEntity: number,
|};
export function uncheckSelection(
    entities: Array<number>,
    lastCheckedEntity: number,
): UncheckAction {
    return {
        type: UNCHECK,
        entities,
        lastCheckedEntity,
    };
}

export default {
    checkSelection,
    performAction,
    resetSelection,
    selectAll,
    toggleSelection,
    uncheckSelection,
};
