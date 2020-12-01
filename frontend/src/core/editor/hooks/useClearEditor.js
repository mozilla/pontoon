/* @flow */

import useUpdateTranslation from './useUpdateTranslation';

/**
 * Return a function to clear the content of the editor.
 */
export default function useClearEditor() {
    const updateTranslation = useUpdateTranslation();

    return () => {
        updateTranslation('');
    };
}
