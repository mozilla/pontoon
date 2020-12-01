/* @flow */

import { useCallback } from 'react';
import { useDispatch } from 'react-redux';

import { actions } from '..';

import type { Translation } from 'core/editor';

/**
 * Return a function to update the content of the editor.
 */
export default function useUpdateTranslation() {
    const dispatch = useDispatch();

    return useCallback(
        (translation: Translation, changeSource?: string) => {
            dispatch(actions.update(translation, changeSource));
        },
        [dispatch],
    );
}
