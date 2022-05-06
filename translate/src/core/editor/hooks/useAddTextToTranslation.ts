import { useCallback } from 'react';

import { useAppDispatch } from '~/hooks';
import { updateSelection } from '../actions';

/**
 * Return a function to add text to the content of the editor.
 */
export function useAddTextToTranslation(): (
  content: string,
  changeSource?: string,
) => void {
  const dispatch = useAppDispatch();

  return useCallback(
    (content: string, changeSource?: string) => {
      dispatch(updateSelection(content, changeSource));
    },
    [dispatch],
  );
}
