/* @flow */

import { createSelector } from 'reselect';

import * as entities from 'core/entities';
import * as plural from 'core/plural';
import { fluent } from 'core/utils';
import * as history from 'modules/history';
import { NAME } from '.';

import type { EntityTranslation, Entity } from 'core/api';
import type { HistoryTranslation, HistoryState } from 'modules/history';
import type { EditorState } from '.';


const editorSelector = (state): EditorState => state[NAME];
const historySelector = (state): HistoryState => state[history.NAME];


export function _existingTranslation(
    editor: EditorState,
    activeTranslation: EntityTranslation,
    history: HistoryState,
    entity: Entity,
): ?(EntityTranslation | HistoryTranslation) {
    const { translation, initialTranslation } = editor;

    let existingTranslation = null;
    if (
        activeTranslation && activeTranslation.pk
        && (
            // If translation is a string, from the generic editor.
            translation === initialTranslation
            // If translation is a FluentMessage, from the fluent editor.
            || (
                translation.equals
                // $FLOW_IGNORE: `equals`, if defined, will always be a function.
                && translation.equals(initialTranslation)
            )
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
            // Except it might actually be a simple Fluent message from the SimpleEditor.
            if (entity.format === 'ftl') {
                // This case happens when the format is Fluent and the string is simple.
                // We thus store a simplified version of the Fluent message in memory,
                // but the history has actual Fluent-formatted strings (with ID).
                // Thus, we need to reconstruct the Fluent message in order to be able
                // to compare it with items in history.
                const reconstructed = fluent.serializer.serializeEntry(
                    fluent.getReconstructedMessage(entity.original, translation)
                );
                existingTranslation = history.translations.find(
                    t => t.string === reconstructed
                )
            }
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
    entities.selectors.getSelectedEntity,
    _existingTranslation
);


export default {
    sameExistingTranslation,
};
