import { useTranslationForEntity } from '~/context/pluralForm';
import { useSelectedEntity } from '~/core/entities/hooks';
import { getReconstructedMessage } from '~/core/utils/fluent/getReconstructedMessage';
import { parser as fluentParser } from '~/core/utils/fluent/parser';
import { serializer as fluentSerializer } from '~/core/utils/fluent/serializer';
import { useAppSelector } from '~/hooks';
import { HISTORY } from '~/modules/history';

import { EDITOR } from '../reducer';

/**
 * Return a Translation identical to the one currently in the Editor.
 *
 * If the content of the Editor is identical to a translation that already
 * exists in the history of the entity, this selector returns that Translation.
 * Othewise, it returns undefined.
 */
export function useExistingTranslation() {
  const initialTranslation = useAppSelector(
    (state) => state[EDITOR].initialTranslation,
  );
  const translation = useAppSelector((state) => state[EDITOR].translation);
  const entity = useSelectedEntity();
  const activeTranslation = useTranslationForEntity(entity);
  const historyTranslations = useAppSelector(
    (state) => state[HISTORY].translations,
  );

  if (
    activeTranslation?.pk &&
    // If translation is a string, from the generic editor.
    (translation === initialTranslation ||
      // If translation is a FluentMessage, from the fluent editor.
      (typeof translation !== 'string' &&
        typeof initialTranslation !== 'string' &&
        translation.equals(initialTranslation)))
  ) {
    return activeTranslation;
  }

  if (historyTranslations.length === 0) {
    return undefined;
  }

  let test: (value: typeof historyTranslations[number]) => boolean;

  if (typeof translation !== 'string') {
    // If translation is a FluentMessage, from the fluent editor.
    //
    // We apply a bunch of logic on the stored translation, to
    // make it work with our Editor. So here, we need to
    // re-serialize it and re-parse it to make sure the translation
    // object is a "clean" one, as produced by Fluent. Otherwise
    // we encounter bugs when comparing it with the history items.
    const entry = fluentParser.parseEntry(
      fluentSerializer.serializeEntry(translation),
    );
    test = (t) => entry.equals(fluentParser.parseEntry(t.string));
  } else if (entity?.format === 'ftl') {
    // If translation is a string, from the generic editor.
    // Except it might actually be a Fluent message from the Simple or Source
    // editors.
    //
    // For Fluent files, the translation can be stored as a simple string
    // when the Source editor or the Simple editor are on. Because of that,
    // we want to turn the string into a Fluent message, as that's simpler
    // to handle and less prone to errors. We do the same for each history
    // entry.
    let entry = fluentParser.parseEntry(translation);
    if (entry.type === 'Junk') {
      // If the message was junk, it means we are likely in the Simple
      // editor, and we thus want to reconstruct the Fluent message.
      // Note that if the user is actually in the Source editor, and
      // entered an invalid value (which creates this junk entry),
      // it doesn't matter as there shouldn't be anything matching anyway.
      entry = getReconstructedMessage(entity.original, translation);
    }
    test = (t) => entry.equals(fluentParser.parseEntry(t.string));
  } else {
    test = (t) => t.string === translation;
  }

  return historyTranslations.find(test);
}
