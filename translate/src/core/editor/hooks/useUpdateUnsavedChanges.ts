import { useEffect, useRef } from 'react';

import { useAppDispatch, useAppSelector } from '~/hooks';
import { useUnsavedChanges } from '~/modules/unsavedchanges';
import {
  hideUnsavedChanges,
  updateUnsavedChanges,
} from '~/modules/unsavedchanges/actions';

export default function useUpdateUnsavedChanges(richEditor: boolean) {
  const dispatch = useAppDispatch();

  const translation = useAppSelector((state) => state.editor.translation);
  const initialTranslation = useAppSelector(
    (state) => state.editor.initialTranslation,
  );
  const { exist, shown } = useUnsavedChanges();

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
      dispatch(updateUnsavedChanges(next));
    }
  }, [richEditor, translation, initialTranslation, exist, dispatch]);

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
    if (!sameTranslation && shown) {
      dispatch(hideUnsavedChanges());
    }
    prevTranslation.current = translation;
  }, [richEditor, translation, prevTranslation, shown, dispatch]);
}
