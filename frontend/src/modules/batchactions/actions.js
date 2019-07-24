/* @flow */


export const CHECK: 'batchactions/CHECK' = 'batchactions/CHECK';
export const TOGGLE: 'batchactions/TOGGLE' = 'batchactions/TOGGLE';
export const RESET: 'batchactions/RESET' = 'batchactions/RESET';
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
    toggleSelection,
    uncheckSelection,
};
