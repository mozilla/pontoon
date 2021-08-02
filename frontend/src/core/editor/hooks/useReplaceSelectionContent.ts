import * as React from 'react';
import { useDispatch } from 'react-redux';

import { useAppSelector } from 'hooks';
import * as editor from 'core/editor';

export default function useReplaceSelectionContent(
    updateTranslationSelectionWith: (...args: Array<any>) => void,
) {
    const dispatch = useDispatch();
    const changeSource = useAppSelector((state) => state.editor.changeSource);
    const selectionReplacementContent = useAppSelector(
        (state) => state.editor.selectionReplacementContent,
    );

    React.useEffect(() => {
        // If there is content to add to the editor, do so, then remove
        // the content so it isn't added again.
        // This is an abuse of the redux store, because we want to update
        // the content differently for each Editor type. Thus each Editor
        // must use this hook and pass it a function specific to its needs.
        if (selectionReplacementContent) {
            updateTranslationSelectionWith(
                selectionReplacementContent,
                changeSource,
            );
            dispatch(editor.actions.resetSelection());
        }
    }, [
        changeSource,
        selectionReplacementContent,
        dispatch,
        updateTranslationSelectionWith,
    ]);
}
