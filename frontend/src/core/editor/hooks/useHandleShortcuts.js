/* @flow */

import { useDispatch, useSelector } from 'react-redux';

import * as editor from 'core/editor';
import * as entities from 'core/entities';
import * as unsavedchanges from 'modules/unsavedchanges';

/**
 * Return a function to handle shortcuts in a translation form.
 */
export default function useHandleShortcuts() {
    const dispatch = useDispatch();

    const clearEditor = editor.useClearEditor();
    const copyMachineryTranslation = editor.useCopyMachineryTranslation();
    const copyOriginalIntoEditor = editor.useCopyOriginalIntoEditor();
    const updateTranslationStatus = editor.useUpdateTranslationStatus();

    const editorState = useSelector((state) => state.editor);
    const unsavedChangesShown = useSelector(
        (state) => state.unsavedchanges.shown,
    );
    const isReadOnlyEditor = useSelector((state) =>
        entities.selectors.isReadOnlyEditor(state),
    );
    const sameExistingTranslation = useSelector((state) =>
        editor.selectors.sameExistingTranslation(state),
    );

    const machineryTranslations = useSelector(
        (state) => state.machinery.translations,
    );

    return (
        event: SyntheticKeyboardEvent<HTMLTextAreaElement>,
        sendTranslation: (
            ignoreWarnings?: boolean,
            translation?: string,
        ) => void,
        clearEditorCustom?: () => void,
        copyOriginalIntoEditorCustom?: () => void,
    ) => {
        const clearEditorFn = clearEditorCustom || clearEditor;
        const copyOriginalIntoEditorFn =
            copyOriginalIntoEditorCustom || copyOriginalIntoEditor;

        const key = event.keyCode;
        let handledEvent = false;

        // Disable keyboard shortcuts when editor is in read only.
        if (isReadOnlyEditor) {
            return;
        }

        // On Enter:
        //   - If unsaved changes popup is shown, proceed.
        //   - If failed checks popup is shown after approving a translation, approve it anyway.
        //   - In other cases, send current translation.
        if (key === 13 && !event.ctrlKey && !event.shiftKey && !event.altKey) {
            handledEvent = true;

            const errors = editorState.errors;
            const warnings = editorState.warnings;
            const source = editorState.source;
            const ignoreWarnings = !!(errors.length || warnings.length);

            // There are unsaved changes, proceed.
            if (unsavedChangesShown) {
                dispatch(unsavedchanges.actions.ignore());
            }
            // Approve anyway.
            else if (typeof source === 'number') {
                updateTranslationStatus(source, 'approve', ignoreWarnings);
            } else if (
                sameExistingTranslation &&
                !sameExistingTranslation.approved
            ) {
                updateTranslationStatus(
                    sameExistingTranslation.pk,
                    'approve',
                    ignoreWarnings,
                );
            }
            // Send translation.
            else {
                sendTranslation(ignoreWarnings);
            }
        }

        // On Esc, close unsaved changes and failed checks popups if open.
        if (key === 27) {
            handledEvent = true;

            const errors = editorState.errors;
            const warnings = editorState.warnings;

            // Close unsaved changes popup
            if (unsavedChangesShown) {
                dispatch(unsavedchanges.actions.hide());
            }
            // Close failed checks popup
            else if (errors.length || warnings.length) {
                dispatch(editor.actions.resetFailedChecks());
            }
        }

        // On Ctrl + Shift + C, copy the original translation.
        if (key === 67 && event.ctrlKey && event.shiftKey && !event.altKey) {
            handledEvent = true;
            copyOriginalIntoEditorFn();
        }

        // On Ctrl + Shift + Backspace, clear the content.
        if (key === 8 && event.ctrlKey && event.shiftKey && !event.altKey) {
            handledEvent = true;
            clearEditorFn();
        }

        // On (Shift+) Tab, copy TM matches into translation.
        if (key === 9) {
            const numTranslations = machineryTranslations.length;
            if (!numTranslations) {
                return;
            }
            const currentIdx = editorState.selectedHelperIndex;
            let nextIdx;
            if (!event.shiftKey) {
                nextIdx = (currentIdx + 1) % numTranslations;
            } else {
                nextIdx = (currentIdx - 1 + numTranslations) % numTranslations;
            }
            const newMachineryTranslation = machineryTranslations[nextIdx];
            dispatch(editor.actions.selectHelperIndex(nextIdx));
            handledEvent = true;
            copyMachineryTranslation(newMachineryTranslation);
        }

        if (handledEvent) {
            event.preventDefault();
        }
    };
}
