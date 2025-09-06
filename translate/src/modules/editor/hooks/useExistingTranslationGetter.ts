import { useContext } from 'react';
import type { HistoryTranslation } from '../../../../src/api/translation';
import { EditorData, useEditorMessageEntry } from '../../../../src/context/Editor';
import { EntityView, useActiveTranslation } from '../../../../src/context/EntityView';
import { HistoryData } from '../../../../src/context/HistoryData';
import { parseEntry, serializeEntry } from '../../../../src/utils/message';
import { pojoEquals } from '../../../../src/utils/pojo';

/**
 * Return a Translation identical to the one currently in the Editor.
 *
 * If the content of the Editor is identical to a translation that already
 * exists in the history of the entity, this selector returns that Translation.
 * Otherwise, it returns undefined.
 */
export function useExistingTranslationGetter() {
  const activeTranslation = useActiveTranslation();
  const { translations } = useContext(HistoryData);
  const { format } = useContext(EntityView).entity;
  const { initial } = useContext(EditorData);
  const entry = useEditorMessageEntry();

  return () => {
    if (activeTranslation?.pk && pojoEquals(initial, entry)) {
      return activeTranslation;
    }

    if (!entry || translations.length === 0) {
      return undefined;
    }

    let test: (value: HistoryTranslation) => boolean;
    if (format === 'fluent') {
      test = (t) => pojoEquals(entry, parseEntry(format, t.string));
    } else {
      try {
        const str = serializeEntry(format, entry);
        test = (t) => t.string === str;
      } catch {
        return undefined;
      }
    }

    return translations.find(test);
  };
}
