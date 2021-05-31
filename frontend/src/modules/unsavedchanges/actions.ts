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
    exist: boolean,
    ignored: boolean,
    callback: (...args: Array<any>) => any,
): (...args: Array<any>) => any {
    return (dispatch) => {
        if (exist && !ignored) {
            dispatch(show(callback));
        } else {
            callback();
        }
    };
}

/**
 * Hide unsaved changes notice.
 */
export type HideAction = {
    readonly type: typeof HIDE;
};
export function hide(): HideAction {
    return {
        type: HIDE,
    };
}

/**
 * Ignore unsaved changes notice ("Proceed").
 */
export type IgnoreAction = {
    readonly type: typeof IGNORE;
};
export function ignore(): IgnoreAction {
    return {
        type: IGNORE,
    };
}

/**
 * Show unsaved changes notice.
 */
export type ShowAction = {
    readonly type: typeof SHOW;
    callback: (...args: Array<any>) => any;
};
export function show(callback: (...args: Array<any>) => any): ShowAction {
    return {
        type: SHOW,
        callback,
    };
}

/**
 * Update unsaved changes status.
 */
export type UpdateAction = {
    readonly exist: boolean;
    readonly type: typeof UPDATE;
};
export function update(exist: boolean): UpdateAction {
    return {
        exist,
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
