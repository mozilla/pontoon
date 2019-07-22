/* @flow */


export const RESET: 'batchactions/RESET' = 'batchactions/RESET';
export const TOGGLE: 'batchactions/TOGGLE' = 'batchactions/TOGGLE';


export type ResetAction = {|
    type: typeof RESET,
|};
export function reset(): ResetAction {
    return {
        type: RESET,
    };
}


export type ToggleAction = {|
    type: typeof TOGGLE,
    entity: number,
|};
export function toggle(entity: number): ToggleAction {
    return {
        type: TOGGLE,
        entity,
    };
}

export default {
    reset,
    toggle,
};
