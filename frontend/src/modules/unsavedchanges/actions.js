/* @flow */

export const HIDE_UNSAVED_CHANGES: 'editor/HIDE_UNSAVED_CHANGES' = 'editor/HIDE_UNSAVED_CHANGES';
export const IGNORE_UNSAVED_CHANGES: 'editor/IGNORE_UNSAVED_CHANGES' = 'editor/IGNORE_UNSAVED_CHANGES';
export const SHOW_UNSAVED_CHANGES: 'editor/SHOW_UNSAVED_CHANGES' = 'editor/SHOW_UNSAVED_CHANGES';


/**
 * Hide unsaved changes notice.
 */
export type HideUnsavedChangesAction = {|
    +type: typeof HIDE_UNSAVED_CHANGES,
|};
export function hideUnsavedChanges(): HideUnsavedChangesAction {
    return {
        type: HIDE_UNSAVED_CHANGES,
    };
}


/**
 * Ignore unsaved changes.
 */
export type IgnoreUnsavedChangesAction = {|
    +type: typeof IGNORE_UNSAVED_CHANGES,
|};
export function ignoreUnsavedChanges(): IgnoreUnsavedChangesAction {
    return {
        type: IGNORE_UNSAVED_CHANGES,
    };
}


/**
 * Show unsaved changes notice.
 */
export type ShowUnsavedChangesAction = {|
    +type: typeof SHOW_UNSAVED_CHANGES,
    unsavedChangesCallback: Function,
|};
export function showUnsavedChanges(unsavedChangesCallback: Function): ShowUnsavedChangesAction {
    return {
        type: SHOW_UNSAVED_CHANGES,
        unsavedChangesCallback,
    };
}


/**
 * Check if the editor has unsaved changes by comparing its content
 * with the active translation. Show unsaved changes if they exist and
 * aren't explicitly ignored, or else execute callback function.
 */
export function checkUnsavedChanges(
    content: string,
    activeTranslation: string,
    unsavedChangesIgnored: boolean,
    callback: Function,
): Function {
    return dispatch => {
        if (!unsavedChangesIgnored && content !== activeTranslation) {
            dispatch(showUnsavedChanges(callback));
            return;
        }

        callback();
    }
}


export default {
    checkUnsavedChanges,
    hideUnsavedChanges,
    ignoreUnsavedChanges,
    showUnsavedChanges,
};
