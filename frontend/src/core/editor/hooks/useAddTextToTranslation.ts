import { useCallback } from 'react';

import { useAppDispatch } from 'hooks';
import { actions } from '..';

/**
 * Return a function to add text to the content of the editor.
 */
export default function useAddTextToTranslation(): (
    content: string,
    changeSource?: string,
) => void {
    const dispatch = useAppDispatch();

    return useCallback(
        (content: string, changeSource?: string) => {
            dispatch(actions.updateSelection(content, changeSource));
        },
        [dispatch],
    );
}
