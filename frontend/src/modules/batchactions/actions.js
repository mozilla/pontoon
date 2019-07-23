/* @flow */


export const RESET: 'batchactions/RESET' = 'batchactions/RESET';
export const TOGGLE: 'batchactions/TOGGLE' = 'batchactions/TOGGLE';


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

export default {
    resetSelection,
    toggleSelection,
};
