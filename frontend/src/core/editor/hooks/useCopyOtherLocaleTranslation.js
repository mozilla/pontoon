/* @flow */

import { useCallback } from 'react';
import { useSelector } from 'react-redux';

import * as entities from 'core/entities';
import type { OtherLocaleTranslation } from 'core/api';

import useUpdateTranslation from './useUpdateTranslation';

/**
 * Return a function to copy the other locale translation into the editor.
 */
export default function useCopyOtherLocaleTranslation() {
    const updateTranslation = useUpdateTranslation();
    const isReadOnlyEditor = useSelector((state) =>
        entities.selectors.isReadOnlyEditor(state),
    );

    return useCallback(
        (translation: OtherLocaleTranslation) => {
            if (isReadOnlyEditor) {
                return;
            }

            // Ignore if selecting text
            if (window.getSelection().toString()) {
                return;
            }

            updateTranslation(translation.translation, 'otherlocales');
        },
        [isReadOnlyEditor, updateTranslation],
    );
}
