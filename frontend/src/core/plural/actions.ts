import { actions as navActions } from 'core/navigation';

import type { Locale } from 'core/locale';

export const RESET: 'plural/RESET' = 'plural/RESET';
export const SELECT: 'plural/SELECT' = 'plural/SELECT';

/**
 * Move to next Entity or pluralForm.
 */
export function moveToNextTranslation(
    dispatch: (...args: Array<any>) => any,
    router: Record<string, any>,
    entity: number,
    nextEntity: number,
    pluralForm: number,
    locale: Locale,
): void {
    if (pluralForm !== -1 && pluralForm < locale.cldrPlurals.length - 1) {
        dispatch(select(pluralForm + 1));
    } else if (nextEntity !== entity) {
        dispatch(navActions.updateEntity(router, nextEntity.toString()));
    }
}

export type ResetAction = {
    type: typeof RESET;
};
export function reset(): ResetAction {
    return {
        type: RESET,
    };
}

export type SelectAction = {
    type: typeof SELECT;
    pluralForm: number;
};
export function select(pluralForm: number): SelectAction {
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
