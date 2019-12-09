/* @flow */

import { createSelector } from 'reselect';

import * as plural from 'core/plural';
import { fluent } from 'core/utils';
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
    const { translation, initialTranslation } = editor;

    let existingTranslation = null;
    if (translation) {
        if (
            // If translation is a string, from the generic editor.
            translation === initialTranslation
            // If translation is a FluentMessage, from the fluent editor.
            || (
                translation.equals
                // $FLOW_IGNORE: `equals`, if defined, will always be a function.
                && translation.equals(initialTranslation)
            )
        ) {
            existingTranslation = activeTranslation;
        }
        else if (history.translations.length) {
            // If translation is a FluentMessage, from the fluent editor.
            if (translation.equals) {
                // We apply a bunch of logic on the stored translation, to
                // make it work with our Editor. So here, we need to
                // re-serialize it and re-parse it to make sure the translation
                // object is a "clean" one, as produced by Fluent. Otherwise
                // we encounter bugs when comparing it with the history items.
                const fluentTranslation = fluent.parser.parseEntry(
                    fluent.serializer.serializeEntry(
                        translation
                    )
                )
                existingTranslation = history.translations.find(
                    t => fluentTranslation.equals(
                        fluent.parser.parseEntry(t.string)
                    )
                )
            }
            // If translation is a string, from the generic editor.
            else {
                existingTranslation = history.translations.find(
                    t => t.string === translation
                )
            }
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
