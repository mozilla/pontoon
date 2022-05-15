import { useCallback, useContext } from 'react';

import { EditorActions } from '~/context/Editor';
import { usePluralForm } from '~/context/PluralForm';
import { useSelectedEntity } from '~/core/entities/hooks';

/**
 * Return a function to copy the original translation into the editor.
 */
export function useCopyOriginalIntoEditor(): () => void {
  const { setEditorFromHistory } = useContext(EditorActions);
  const entity = useSelectedEntity();
  const { pluralForm } = usePluralForm(entity);

  return useCallback(() => {
    if (entity) {
      setEditorFromHistory(
        pluralForm > 0 ? entity.original_plural : entity.original,
      );
    }
  }, [entity, pluralForm]);
}
