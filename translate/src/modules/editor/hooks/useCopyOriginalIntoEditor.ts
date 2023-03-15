import { useCallback, useContext } from 'react';

import { EditorActions } from '~/context/Editor';
import { useEntitySource } from '~/context/EntityView';

/**
 * Return a function to copy the original translation into the editor.
 */
export function useCopyOriginalIntoEditor(): () => void {
  const { setEditorFromHistory } = useContext(EditorActions);
  const source = useEntitySource();
  return useCallback(
    () => setEditorFromHistory(source),
    [setEditorFromHistory, source],
  );
}
