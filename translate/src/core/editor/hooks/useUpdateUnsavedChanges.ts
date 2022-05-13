import { useContext, useEffect, useRef } from 'react';
import { UnsavedChanges } from '~/context/UnsavedChanges';

import { useAppSelector } from '~/hooks';

export function useUpdateUnsavedChanges(richEditor: boolean) {
  const translation = useAppSelector((state) => state.editor.translation);
  const initialTranslation = useAppSelector(
    (state) => state.editor.initialTranslation,
  );
  const { exist, show, set } = useContext(UnsavedChanges);

  // When the translation or the initial translation changes, check for unsaved changes.
  useEffect(() => {
    let next: boolean;
    if (typeof translation === 'string') {
      if (richEditor) {
        return;
      }
      next = translation !== initialTranslation;
    } else {
      next =
        typeof initialTranslation !== 'string' &&
        !translation.equals(initialTranslation);
    }

    if (next !== exist) {
      set({ exist: next, ignore: false });
    }
  }, [richEditor, translation, initialTranslation, exist]);

  // When the translation changes, hide unsaved changes notice.
  // We need to track the translation value, because this hook depends on the
  // `shown` value of the unsavedchanges module, but we don't want to hide
  // the notice automatically after it's displayed. We thus only update when
  // the translation has effectively changed.
  const prevTranslation = useRef(translation);
  useEffect(() => {
    let sameTranslation;
    if (richEditor) {
      if (typeof translation === 'string') {
        return;
      }
      sameTranslation =
        typeof prevTranslation.current !== 'string' &&
        translation.equals(prevTranslation.current);
    } else {
      sameTranslation = prevTranslation.current === translation;
    }
    if (!sameTranslation && show) {
      set(null);
    }
    prevTranslation.current = translation;
  }, [richEditor, translation, prevTranslation, show]);
}
