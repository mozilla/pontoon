/* @flow */

import type { Translation } from 'core/editor';
import type { UnsavedChangesState } from './reducer';

export const HIDE: 'unsavedchanges/HIDE' = 'unsavedchanges/HIDE';
export const IGNORE: 'unsavedchanges/IGNORE' = 'unsavedchanges/IGNORE';
export const SHOW: 'unsavedchanges/SHOW' = 'unsavedchanges/SHOW';
export const UPDATE: 'unsavedchanges/UPDATE' = 'unsavedchanges/UPDATE';

/**
 * Check if the editor has unsaved changes by comparing its content
 * with the active translation. Show unsaved changes if they exist and
 * aren't explicitly ignored, or else execute callback function.
 */
export function check(
    unsavedchanges: UnsavedChangesState,
    callback: Function,
): Function {
    return (dispatch) => {
        if (unsavedchanges.exist && !unsavedchanges.ignored) {
            dispatch(show(callback));
        } else {
            callback();
        }
    };
}

/**
 * Hide unsaved changes notice.
 */
export type HideAction = {|
    +type: typeof HIDE,
|};
export function hide(): HideAction {
    return {
        type: HIDE,
    };
}

/**
 * Ignore unsaved changes notice ("Proceed").
 */
export type IgnoreAction = {|
    +type: typeof IGNORE,
|};
export function ignore(): IgnoreAction {
    return {
        type: IGNORE,
    };
}

/**
 * Show unsaved changes notice.
 */
export type ShowAction = {|
    +type: typeof SHOW,
    callback: Function,
|};
export function show(callback: Function): ShowAction {
    return {
        type: SHOW,
        callback,
    };
}

/**
 * Update unsaved changes status.
 */
export type UpdateAction = {|
    +exist: boolean,
    +type: typeof UPDATE,
|};
export function update(
    editorTranslation: Translation,
    initialTranslation: Translation,
): UpdateAction {
    return {
        exist: editorTranslation !== initialTranslation,
        type: UPDATE,
    };
}

export default {
    check,
    hide,
    ignore,
    show,
    update,
};
