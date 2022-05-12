import { useCallback } from 'react';

import type { MachineryTranslation, SourceType } from '~/api/machinery';
import { EDITOR } from '../reducer';
import { useAppDispatch, useAppSelector } from '~/hooks';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';

import { updateMachinerySources } from '../actions';
import { useAddTextToTranslation } from './useAddTextToTranslation';
import { useUpdateTranslation } from './useUpdateTranslation';

/**
 * Return a function to copy the original translation into the editor.
 */
export function useCopyMachineryTranslation(
  entity?: number | null,
): (translation: MachineryTranslation) => void {
  const dispatch = useAppDispatch();

  const addTextToTranslation = useAddTextToTranslation();
  const updateTranslation = useUpdateTranslation();
  const updateMachinerySources_ = useCallback(
    (machinerySources: Array<SourceType>, machineryTranslation: string) => {
      dispatch(updateMachinerySources(machinerySources, machineryTranslation));
    },
    [dispatch],
  );

  const readonly = useReadonlyEditor();
  const translation = useAppSelector((state) => state[EDITOR].translation);
  const isFluentTranslationMessage = typeof translation !== 'string';

  return useCallback(
    (translation: MachineryTranslation) => {
      if (readonly) {
        return;
      }

      // Ignore if selecting text
      if (window.getSelection()?.toString()) {
        return;
      }

      // If there is no entity then it is a search term and it is
      // added to the editor instead of replacing the editor content
      if (!entity) {
        addTextToTranslation(translation.translation);
      }
      // This is a Fluent Message, thus we are in the RichEditor.
      // Handle machinery differently.
      else if (isFluentTranslationMessage) {
        addTextToTranslation(translation.translation, 'machinery');
      }
      // By default replace editor content
      else {
        updateTranslation(translation.translation, 'machinery');
      }
      updateMachinerySources_(translation.sources, translation.translation);
    },
    [
      isFluentTranslationMessage,
      readonly,
      entity,
      addTextToTranslation,
      updateTranslation,
      updateMachinerySources_,
    ],
  );
}
