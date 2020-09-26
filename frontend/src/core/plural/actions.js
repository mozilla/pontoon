/* @flow */

import { actions as navActions } from 'core/navigation';

import type { Locale } from 'core/locale';

export const RESET: 'plural/RESET' = 'plural/RESET';
export const SELECT: 'plural/SELECT' = 'plural/SELECT';

/**
 * Move to next Entity or pluralForm.
 */
export function moveToNextTranslation(
    dispatch: Function,
    router: Object,
    entity: number,
    nextEntity: number,
    pluralForm: number,
    locale: Locale,
): Function {
    if (pluralForm !== -1 && pluralForm < locale.cldrPlurals.length - 1) {
        dispatch(select(pluralForm + 1));
    } else if (nextEntity !== entity) {
        dispatch(navActions.updateEntity(router, nextEntity.toString()));
    }
}

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
    moveToNextTranslation,
    reset,
    select,
};
