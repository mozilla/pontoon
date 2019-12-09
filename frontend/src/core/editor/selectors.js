/* @flow */

import { createSelector } from 'reselect';

import * as plural from 'core/plural';
import * as history from 'modules/history';
import { NAME } from '.';

import type { EntityTranslation } from 'core/api';
import type { HistoryTranslation, HistoryState } from 'modules/history';
import type { EditorState } from '.';


const editorSelector = (state): EditorState => state[NAME];
const historySelector = (state): HistoryState => state[history.NAME];


export function _existingTranslation(
    editor: EditorState,
    activeTranslation: EntityTranslation,
    history: HistoryState,
): ?(EntityTranslation | HistoryTranslation) {
    let existingTranslation = null;
    if (editor.translation) {
        if (editor.translation === editor.initialTranslation) {
            existingTranslation = activeTranslation;
        }
        else if (history.translations.length) {
            existingTranslation = history.translations.find(
                t => t.string === editor.translation
            )
        }
    }
    return existingTranslation;
}


/**
 * Return a Translation identical to the one currently in the Editor.
 *
 * If the content of the Editor is identical to a translation that already
 * exists in the history of the entity, this selector returns that Translation.
 * Othewise, it returns null.
 */
export const sameExistingTranslation: Function = createSelector(
    editorSelector,
    plural.selectors.getTranslationForSelectedEntity,
    historySelector,
    _existingTranslation
);


export default {
    sameExistingTranslation,
};
