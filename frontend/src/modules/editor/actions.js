/* @flow */

import api from 'core/api';

import { actions as navActions } from 'core/navigation';
import { actions as entitiesActions } from 'modules/entitieslist';

import type { DbEntity } from 'modules/entitieslist';


export const RESET_SELECTION: 'editor/RESET_SELECTION' = 'editor/RESET_SELECTION';
export const UPDATE: 'editor/UPDATE' = 'editor/UPDATE';
export const UPDATE_SELECTION: 'editor/UPDATE_SELECTION' = 'editor/UPDATE_SELECTION';


/**
 * Update the current translation of the selected entity.
 */
export type UpdateAction = {|
    +type: typeof UPDATE,
    +translation: string,
|};
export function update(translation: string): UpdateAction {
    return {
        type: UPDATE,
        translation,
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
 * Update the content that should replace the currently selected text in the
 * active editor.
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
 * Save the current translation.
 */
export function sendTranslation(
    entity: number,
    translation: string,
    locale: string,
    original: string,
    pluralForm: number,
    forceSuggestions: boolean,
    nextEntity: ?DbEntity,
    router: Object,
): Function {
    return async dispatch => {
        const content = await api.translation.updateTranslation(
            entity,
            translation,
            locale,
            pluralForm,
            original,
            forceSuggestions,
        );

        if (content.same) {
            // The translation that was provided is the same as an existing
            // translation for that entity.
            // Show an error.
            console.error('Same Translation Error');
        }
        else if (
            content.type === 'added' ||
            content.type === 'saved' ||
            content.type === 'updated'
        ) {
            dispatch(
                entitiesActions.updateEntityTranslation(
                    entity,
                    pluralForm,
                    content.translation
                )
            );

            if (nextEntity && nextEntity.pk !== entity) {
                // The change did work, we want to move on to the next Entity.
                dispatch(navActions.updateEntity(router, nextEntity.pk.toString()));
            }
        }
    }
}


export default {
    resetSelection,
    sendTranslation,
    update,
    updateSelection,
};
