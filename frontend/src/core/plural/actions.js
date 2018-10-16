/* @flow */

export const RESET: 'plural/RESET' = 'plural/RESET';
export const SELECT: 'plural/SELECT' = 'plural/SELECT';


export type ResetAction = {|
    type: typeof RESET,
|};
export function reset() {
    return {
        type: RESET,
    };
}


export type SelectAction = {|
    type: typeof SELECT,
    pluralForm: number,
|};
export function select(pluralForm: number) {
    return {
        type: SELECT,
        pluralForm,
    };
}


export default {
    reset,
    select,
};
