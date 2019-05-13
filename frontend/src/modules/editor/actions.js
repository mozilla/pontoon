/* @flow */

import api from 'core/api';

import * as notification from 'core/notification';
import { actions as pluralActions } from 'core/plural';
import { actions as entitiesActions } from 'modules/entitieslist';

import type { DbEntity } from 'modules/entitieslist';
import type { Locale } from 'core/locales';


export const HIDE_UNSAVED_CHANGES: 'editor/HIDE_UNSAVED_CHANGES' = 'editor/HIDE_UNSAVED_CHANGES';
export const IGNORE_UNSAVED_CHANGES: 'editor/IGNORE_UNSAVED_CHANGES' = 'editor/IGNORE_UNSAVED_CHANGES';
export const RESET_FAILED_CHECKS: 'editor/RESET_FAILED_CHECKS' = 'editor/RESET_FAILED_CHECKS';
export const RESET_SELECTION: 'editor/RESET_SELECTION' = 'editor/RESET_SELECTION';
export const SHOW_UNSAVED_CHANGES: 'editor/SHOW_UNSAVED_CHANGES' = 'editor/SHOW_UNSAVED_CHANGES';
export const UPDATE: 'editor/UPDATE' = 'editor/UPDATE';
export const UPDATE_FAILED_CHECKS: 'editor/UPDATE_FAILED_CHECKS' = 'editor/UPDATE_FAILED_CHECKS';
export const UPDATE_SELECTION: 'editor/UPDATE_SELECTION' = 'editor/UPDATE_SELECTION';


/**
 * Update the current translation of the selected entity.
 */
export type UpdateAction = {|
    +type: typeof UPDATE,
    +translation: string,
    +changeSource: string,
|};
export function update(translation: string, changeSource?: string): UpdateAction {
    return {
        type: UPDATE,
        translation,
        changeSource: changeSource || 'internal',
    };
}


/**
 * Update the content that should replace the currently selected text in the
 * active editor.
 */
export type UpdateSelectionAction = {|
    +type: typeof UPDATE_SELECTION,
    +content: string,
|};
export function updateSelection(content: string): UpdateSelectionAction {
    return {
        type: UPDATE_SELECTION,
        content,
    };
}


/**
 * Update failed checks in the active editor.
 */
export type FailedChecks = {|
    +clErrors: Array<string>,
    +pErrors: Array<string>,
    +clWarnings: Array<string>,
    +pndbWarnings: Array<string>,
    +ttWarnings: Array<string>,
|};
export type UpdateFailedChecksAction = {|
    +type: typeof UPDATE_FAILED_CHECKS,
    +failedChecks: FailedChecks,
    +source: '' | 'stored' | 'submitted' | number,
|};
export function updateFailedChecks(
    failedChecks: FailedChecks,
    source: '' | 'stored' | 'submitted' | number,
): UpdateFailedChecksAction {
    return {
        type: UPDATE_FAILED_CHECKS,
        failedChecks,
        source,
    };
}


/**
 * Reset content to default value.
 */
export type ResetSelectionAction = {|
    +type: typeof RESET_SELECTION,
|};
export function resetSelection(): ResetSelectionAction {
    return {
        type: RESET_SELECTION,
    };
}


/**
 * Reset failed checks to default value.
 */
export type ResetFailedChecksAction = {|
    +type: typeof RESET_FAILED_CHECKS,
|};
export function resetFailedChecks(): ResetFailedChecksAction {
    return {
        type: RESET_FAILED_CHECKS,
    };
}


function _getOperationNotif(change: 'added' | 'saved' | 'updated') {
    switch (change) {
        case 'added':
            return notification.messages.TRANSLATION_ADDED;
        case 'saved':
            return notification.messages.TRANSLATION_SAVED;
        case 'updated':
            return notification.messages.TRANSLATION_UPDATED;
        default:
            throw new Error('Unexpected translation status change: ' + change);
    }
}


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
 * Save the current translation.
 */
export function sendTranslation(
    entity: number,
    translation: string,
    locale: Locale,
    original: string,
    pluralForm: number,
    forceSuggestions: boolean,
    nextEntity: ?DbEntity,
    router: Object,
    ignoreWarnings: ?boolean,
): Function {
    return async dispatch => {
        const content = await api.translation.updateTranslation(
            entity,
            translation,
            locale.code,
            pluralForm,
            original,
            forceSuggestions,
            ignoreWarnings,
        );

        if (content.failedChecks) {
            dispatch(updateFailedChecks(content.failedChecks, 'submitted'));
        }
        else if (content.same) {
            // The translation that was provided is the same as an existing
            // translation for that entity.
            dispatch(
                notification.actions.add(
                    notification.messages.SAME_TRANSLATION
                )
            );
        }
        else if (
            content.type === 'added' ||
            content.type === 'saved' ||
            content.type === 'updated'
        ) {
            // Notify the user of the change that happened.
            const notif = _getOperationNotif(content.type);
            dispatch(notification.actions.add(notif));

            dispatch(
                entitiesActions.updateEntityTranslation(
                    entity,
                    pluralForm,
                    content.translation
                )
            );
            if (nextEntity) {
                // The change did work, we want to move on to the next Entity or pluralForm.
                pluralActions.moveToNextTranslation(
                    dispatch,
                    router,
                    entity,
                    nextEntity.pk,
                    pluralForm,
                    locale,
                );
            }
        }
    }
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
    resetFailedChecks,
    resetSelection,
    sendTranslation,
    showUnsavedChanges,
    update,
    updateFailedChecks,
    updateSelection,
};
