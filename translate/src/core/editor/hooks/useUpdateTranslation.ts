import { useCallback } from 'react';

import type { Translation } from '~/core/editor';
import { useAppDispatch } from '~/hooks';

import { updateTranslation } from '../actions';

/**
 * Return a function to update the content of the editor.
 */
export function useUpdateTranslation(): (
  translation: Translation,
  changeSource?: string,
) => void {
  const dispatch = useAppDispatch();

  return useCallback(
    (translation: Translation, changeSource?: string) => {
      dispatch(updateTranslation(translation, changeSource));
    },
    [dispatch],
  );
}
