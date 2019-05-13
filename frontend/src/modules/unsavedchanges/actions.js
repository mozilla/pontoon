/* @flow */

export const HIDE: 'editor/HIDE' = 'editor/HIDE';
export const IGNORE: 'editor/IGNORE' = 'editor/IGNORE';
export const SHOW: 'editor/SHOW' = 'editor/SHOW';


/**
 * Check if the editor has unsaved changes by comparing its content
 * with the active translation. Show unsaved changes if they exist and
 * aren't explicitly ignored, or else execute callback function.
 */
export function check(
    content: string,
    activeTranslation: string,
    ignored: boolean,
    callback: Function,
): Function {
    return dispatch => {
        if (!ignored && content !== activeTranslation) {
            dispatch(show(callback));
            return;
        }

        callback();
    }
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
 * Ignore unsaved changes notice ("Leave anyway").
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


export default {
    check,
    hide,
    ignore,
    show,
};
