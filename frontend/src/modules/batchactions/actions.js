/* @flow */

import api from 'core/api';


export const CHECK: 'batchactions/CHECK' = 'batchactions/CHECK';
export const RESET: 'batchactions/RESET' = 'batchactions/RESET';
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
    resetSelection,
    selectAll,
    toggleSelection,
    uncheckSelection,
};
