/* @flow */

import { useCallback } from 'react';
import { useDispatch, useSelector } from 'react-redux';

import { actions } from '..';

import * as entities from 'core/entities';
import type { MachineryTranslation, SourceType } from 'core/api';

import useAddTextToTranslation from './useAddTextToTranslation';
import useUpdateTranslation from './useUpdateTranslation';

/**
 * Return a function to copy the original translation into the editor.
 */
export default function useCopyMachineryTranslation() {
    const dispatch = useDispatch();

    const addTextToTranslation = useAddTextToTranslation();
    const updateTranslation = useUpdateTranslation();
    const updateMachinerySources = useCallback(
        (machinerySources: Array<SourceType>, machineryTranslation: string) => {
            dispatch(
                actions.updateMachinerySources(
                    machinerySources,
                    machineryTranslation,
                ),
            );
        },
        [dispatch],
    );

    const editorContent = useSelector((state) => state.editor.translation);
    const isReadOnlyEditor = useSelector((state) =>
        entities.selectors.isReadOnlyEditor(state),
    );
    const entity = useSelector((state) =>
        entities.selectors.getSelectedEntity(state),
    );

    return useCallback(
        (translation: MachineryTranslation) => {
            if (isReadOnlyEditor) {
                return;
            }

            // Ignore if selecting text
            if (window.getSelection().toString()) {
                return;
            }

            // If there is no entity then it is a search term and it is
            // added to the editor instead of replacing the editor content
            if (!entity) {
                addTextToTranslation(translation.translation);
            }
            // This is a Fluent Message, thus we are in the RichEditor.
            // Handle machinery differently.
            else if (typeof editorContent !== 'string') {
                addTextToTranslation(translation.translation, 'machinery');
            }
            // By default replace editor content
            else {
                updateTranslation(translation.translation, 'machinery');
            }
            updateMachinerySources(
                translation.sources,
                translation.translation,
            );
        },
        [
            isReadOnlyEditor,
            entity,
            editorContent,
            addTextToTranslation,
            updateTranslation,
            updateMachinerySources,
        ],
    );
}
