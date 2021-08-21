import { useCallback } from 'react';

import { actions } from '..';

import type { Translation } from 'core/editor';
import { useAppDispatch } from 'hooks';

/**
 * Return a function to update the content of the editor.
 */
export default function useUpdateTranslation(): (
    translation: Translation,
    changeSource?: string,
) => void {
    const dispatch = useAppDispatch();

    return useCallback(
        (translation: Translation, changeSource?: string) => {
            dispatch(actions.update(translation, changeSource));
        },
        [dispatch],
    );
}
