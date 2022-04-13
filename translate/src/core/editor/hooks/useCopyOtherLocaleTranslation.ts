import { useCallback } from 'react';
import type { OtherLocaleTranslation } from '~/core/api';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';
import useUpdateTranslation from './useUpdateTranslation';

/**
 * Return a function to copy the other locale translation into the editor.
 */
export default function useCopyOtherLocaleTranslation(): (
  translation: OtherLocaleTranslation,
) => void {
  const updateTranslation = useUpdateTranslation();
  const readonly = useReadonlyEditor();

  return useCallback(
    (translation: OtherLocaleTranslation) => {
      if (readonly) {
        return;
      }

      // Ignore if selecting text
      if (window.getSelection()?.toString()) {
        return;
      }

      updateTranslation(translation.translation, 'otherlocales');
    },
    [readonly, updateTranslation],
  );
}
