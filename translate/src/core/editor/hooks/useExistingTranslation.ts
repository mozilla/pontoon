import { useContext } from 'react';

import { EditorData, getFluentEntry } from '~/context/Editor';
import { useTranslationForEntity } from '~/context/PluralForm';
import { useSelectedEntity } from '~/core/entities/hooks';
import { parseEntry } from '~/core/utils/fluent/parser';
import { useAppSelector } from '~/hooks';
import { HISTORY } from '~/modules/history/reducer';

/**
 * Return a Translation identical to the one currently in the Editor.
 *
 * If the content of the Editor is identical to a translation that already
 * exists in the history of the entity, this selector returns that Translation.
 * Othewise, it returns undefined.
 */
export function useExistingTranslation() {
  const entity = useSelectedEntity();
  const activeTranslation = useTranslationForEntity(entity);
  const historyTranslations = useAppSelector(
    (state) => state[HISTORY].translations,
  );
  const editor = useContext(EditorData);
  const { format, initial, value } = editor;

  if (
    activeTranslation?.pk &&
    // If translation is a string, from the generic editor.
    (value === initial ||
      // If translation is a FluentMessage, from the fluent editor.
      (typeof value !== 'string' && value.equals(parseEntry(initial))))
  ) {
    return activeTranslation;
  }

  if (historyTranslations.length === 0) {
    return undefined;
  }

  let test: (value: typeof historyTranslations[number]) => boolean;
  if (format === 'ftl') {
    const entry = getFluentEntry(editor);
    test = (t) => entry.equals(parseEntry(t.string));
  } else {
    test = (t) => t.string === value;
  }

  return historyTranslations.find(test);
}
