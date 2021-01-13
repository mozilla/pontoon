/* @flow */

import { useCallback } from 'react';
import { useDispatch } from 'react-redux';

import { actions } from '..';

/**
 * Return a function to add text to the content of the editor.
 */
export default function useAddTextToTranslation() {
    const dispatch = useDispatch();

    return useCallback(
        (content: string, changeSource?: string) => {
            dispatch(actions.updateSelection(content, changeSource));
        },
        [dispatch],
    );
}
