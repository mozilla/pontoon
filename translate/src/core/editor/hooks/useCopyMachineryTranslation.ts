import { useCallback } from 'react';

import type { MachineryTranslation, SourceType } from '~/core/api';
import { NAME as EDITOR } from '~/core/editor';
import { useAppDispatch, useAppSelector } from '~/hooks';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';

import actions from '../actions';
import useAddTextToTranslation from './useAddTextToTranslation';
import useUpdateTranslation from './useUpdateTranslation';

/**
 * Return a function to copy the original translation into the editor.
 */
export default function useCopyMachineryTranslation(
  entity?: number | null,
): (translation: MachineryTranslation) => void {
  const dispatch = useAppDispatch();

  const addTextToTranslation = useAddTextToTranslation();
  const updateTranslation = useUpdateTranslation();
  const updateMachinerySources = useCallback(
    (machinerySources: Array<SourceType>, machineryTranslation: string) => {
      dispatch(
        actions.updateMachinerySources(machinerySources, machineryTranslation),
      );
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
      updateMachinerySources(translation.sources, translation.translation);
    },
    [
      isFluentTranslationMessage,
      readonly,
      entity,
      addTextToTranslation,
      updateTranslation,
      updateMachinerySources,
    ],
  );
}
