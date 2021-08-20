import * as React from 'react';
import { useDispatch } from 'react-redux';

import { useAppSelector } from 'hooks';
import * as unsavedchanges from 'modules/unsavedchanges';

export default function useUpdateUnsavedChanges(richEditor: boolean) {
    const dispatch = useDispatch();

    const translation = useAppSelector((state) => state.editor.translation);
    const initialTranslation = useAppSelector(
        (state) => state.editor.initialTranslation,
    );
    const unsavedChangesExist = useAppSelector(
        (state) => state.unsavedchanges.exist,
    );
    const unsavedChangesShown = useAppSelector(
        (state) => state.unsavedchanges.shown,
    );

    // When the translation or the initial translation changes, check for unsaved changes.
    React.useEffect(() => {
        let exist;
        if (richEditor) {
            if (typeof translation === 'string') {
                return;
            }
            exist =
                typeof initialTranslation !== 'string' &&
                !translation.equals(initialTranslation);
        } else {
            exist = translation !== initialTranslation;
        }

        if (exist !== unsavedChangesExist) {
            dispatch(unsavedchanges.actions.update(exist));
        }
    }, [
        richEditor,
        translation,
        initialTranslation,
        unsavedChangesExist,
        dispatch,
    ]);

    // When the translation changes, hide unsaved changes notice.
    // We need to track the translation value, because this hook depends on the
    // `shown` value of the unsavedchanges module, but we don't want to hide
    // the notice automatically after it's displayed. We thus only update when
    // the translation has effectively changed.
    const prevTranslation = React.useRef(translation);
    React.useEffect(() => {
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
        if (!sameTranslation && unsavedChangesShown) {
            dispatch(unsavedchanges.actions.hide());
        }
        prevTranslation.current = translation;
    }, [
        richEditor,
        translation,
        prevTranslation,
        unsavedChangesShown,
        dispatch,
    ]);
}
