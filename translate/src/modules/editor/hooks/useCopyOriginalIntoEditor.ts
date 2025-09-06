import { useCallback, useContext } from 'react';

import { EditorActions } from '../../../../src/context/Editor';
import { EntityView } from '../../../../src/context/EntityView';

/**
 * Return a function to copy the original translation into the editor.
 */
export function useCopyOriginalIntoEditor(): () => void {
  const { setEditorFromHistory } = useContext(EditorActions);
  const source = useContext(EntityView).entity.original;
  return useCallback(
    () => setEditorFromHistory(source),
    [setEditorFromHistory, source],
  );
}
