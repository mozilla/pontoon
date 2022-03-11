import { createSelector } from 'reselect';

import * as entities from '~/core/entities';
import * as plural from '~/core/plural';
import { fluent } from '~/core/utils';
import * as history from '~/modules/history';
import { NAME } from '.';

import type { RootState } from '../../store';

const editorSelector = (state: RootState) => state[NAME];
const historySelector = (state: RootState) => state[history.NAME];

export function _existingTranslation(
  editor: ReturnType<typeof editorSelector>,
  activeTranslation: ReturnType<
    typeof plural.selectors.getTranslationForSelectedEntity
  >,
  history: ReturnType<typeof historySelector>,
  entity: ReturnType<typeof entities.selectors.getSelectedEntity>,
) {
  const { translation, initialTranslation } = editor;

  if (
    activeTranslation &&
    activeTranslation.pk &&
    // If translation is a string, from the generic editor.
    (translation === initialTranslation ||
      // If translation is a FluentMessage, from the fluent editor.
      (typeof translation !== 'string' &&
        typeof initialTranslation !== 'string' &&
        translation.equals(initialTranslation)))
  ) {
    return activeTranslation;
  }
  if (history.translations.length === 0) {
    return undefined;
  }
  // If translation is a FluentMessage, from the fluent editor.
  if (typeof translation !== 'string') {
    // We apply a bunch of logic on the stored translation, to
    // make it work with our Editor. So here, we need to
    // re-serialize it and re-parse it to make sure the translation
    // object is a "clean" one, as produced by Fluent. Otherwise
    // we encounter bugs when comparing it with the history items.
    const fluentTranslation = fluent.parser.parseEntry(
      fluent.serializer.serializeEntry(translation),
    );
    return history.translations.find((t) =>
      fluentTranslation.equals(fluent.parser.parseEntry(t.string)),
    );
  }
  // If translation is a string, from the generic editor.
  // Except it might actually be a Fluent message from the Simple or Source
  // editors.
  if (entity?.format === 'ftl') {
    // For Fluent files, the translation can be stored as a simple string
    // when the Source editor or the Simple editor are on. Because of that,
    // we want to turn the string into a Fluent message, as that's simpler
    // to handle and less prone to errors. We do the same for each history
    // entry.
    let fluentTranslation = fluent.parser.parseEntry(translation);
    if (fluentTranslation.type === 'Junk') {
      // If the message was junk, it means we are likely in the Simple
      // editor, and we thus want to reconstruct the Fluent message.
      // Note that if the user is actually in the Source editor, and
      // entered an invalid value (which creates this junk entry),
      // it doesn't matter as there shouldn't be anything matching anyway.
      fluentTranslation = fluent.getReconstructedMessage(
        entity.original,
        translation,
      );
    }
    return history.translations.find((t) =>
      fluentTranslation.equals(fluent.parser.parseEntry(t.string)),
    );
  }
  return history.translations.find((t) => t.string === translation);
}

/**
 * Return a Translation identical to the one currently in the Editor.
 *
 * If the content of the Editor is identical to a translation that already
 * exists in the history of the entity, this selector returns that Translation.
 * Othewise, it returns null.
 */
export const sameExistingTranslation = createSelector(
  editorSelector,
  plural.selectors.getTranslationForSelectedEntity,
  historySelector,
  entities.selectors.getSelectedEntity,
  _existingTranslation,
);

function _isFluentMessage(editorState: ReturnType<typeof editorSelector>) {
  return typeof editorState.translation !== 'string';
}

/**
 * Returns `true` if the current editor translation contains a Fluent message.
 */
const isFluentTranslationMessage = createSelector(
  editorSelector,
  _isFluentMessage,
);

export default {
  sameExistingTranslation,
  isFluentTranslationMessage,
};
