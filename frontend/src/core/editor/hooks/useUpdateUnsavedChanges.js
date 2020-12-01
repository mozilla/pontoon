import * as React from 'react';
import { useDispatch, useSelector } from 'react-redux';

import * as unsavedchanges from 'modules/unsavedchanges';

export default function useUpdateUnsavedChanges(richEditor: boolean) {
    const dispatch = useDispatch();

    const translation = useSelector((state) => state.editor.translation);
    const initialTranslation = useSelector(
        (state) => state.editor.initialTranslation,
    );
    const unsavedChangesExist = useSelector(
        (state) => state.unsavedchanges.exist,
    );
    const unsavedChangesShown = useSelector(
        (state) => state.unsavedchanges.shown,
    );

    // When the translation or the initial translation changes, check for unsaved changes.
    React.useEffect(() => {
        if (richEditor && typeof translation === 'string') {
            return;
        }

        let exist;
        if (richEditor) {
            exist = !translation.equals(initialTranslation);
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
        if (richEditor && typeof translation === 'string') {
            return;
        }

        let sameTranslation;
        if (richEditor) {
            sameTranslation = translation.equals(prevTranslation.current);
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
