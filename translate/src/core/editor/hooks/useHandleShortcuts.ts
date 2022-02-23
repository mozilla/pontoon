import { useAppDispatch, useAppSelector } from '~/hooks';
import * as editor from '~/core/editor';
import * as entities from '~/core/entities';
import * as unsavedchanges from '~/modules/unsavedchanges';

/**
 * Return a function to handle shortcuts in a translation form.
 */
export default function useHandleShortcuts(): (
  event: React.KeyboardEvent<HTMLTextAreaElement>,
  sendTranslation: (ignoreWarnings?: boolean, translation?: string) => void,
  clearEditorCustom?: () => void,
  copyOriginalIntoEditorCustom?: () => void,
) => void {
  const dispatch = useAppDispatch();

  const clearEditor = editor.useClearEditor();
  const copyMachineryTranslation = editor.useCopyMachineryTranslation();
  const copyOriginalIntoEditor = editor.useCopyOriginalIntoEditor();
  const copyOtherLocaleTranslation = editor.useCopyOtherLocaleTranslation();
  const updateTranslationStatus = editor.useUpdateTranslationStatus();

  const editorState = useAppSelector((state) => state.editor);
  const unsavedChangesShown = useAppSelector(
    (state) => state.unsavedchanges.shown,
  );
  const isReadOnlyEditor = useAppSelector((state) =>
    entities.selectors.isReadOnlyEditor(state),
  );
  const sameExistingTranslation = useAppSelector((state) =>
    editor.selectors.sameExistingTranslation(state),
  );

  const machineryTranslations = useAppSelector(
    (state) => state.machinery.translations,
  );
  const concordanceSearchResults = useAppSelector(
    (state) => state.machinery.searchResults,
  );
  const otherLocaleTranslations = useAppSelector(
    (state) => state.otherlocales.translations,
  );

  return (
    event: React.KeyboardEvent<HTMLTextAreaElement>,
    sendTranslation: (ignoreWarnings?: boolean, translation?: string) => void,
    clearEditorCustom?: () => void,
    copyOriginalIntoEditorCustom?: () => void,
  ) => {
    const clearEditorFn = clearEditorCustom || clearEditor;
    const copyOriginalIntoEditorFn =
      copyOriginalIntoEditorCustom || copyOriginalIntoEditor;

    const key = event.keyCode;

    // Disable keyboard shortcuts when editor is in read only.
    if (isReadOnlyEditor) {
      return;
    }

    // On Enter:
    //   - If unsaved changes popup is shown, proceed.
    //   - If failed checks popup is shown after approving a translation, approve it anyway.
    //   - In other cases, send current translation.
    if (key === 13 && !event.ctrlKey && !event.shiftKey && !event.altKey) {
      event.preventDefault();

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
      } else if (sameExistingTranslation && !sameExistingTranslation.approved) {
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
      event.preventDefault();

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
      event.preventDefault();
      copyOriginalIntoEditorFn();
    }

    // On Ctrl + Shift + Backspace, clear the content.
    if (key === 8 && event.ctrlKey && event.shiftKey && !event.altKey) {
      event.preventDefault();
      clearEditorFn();
    }

    // On Ctrl + Shift + Up/Down, copy next/previous entry from active
    // helper tab (Machinery or Locales) into translation.
    if (event.ctrlKey && event.shiftKey && !event.altKey) {
      if (key !== 38 && key !== 40) {
        return;
      }

      const isMachinery = editorState.selectedHelperTabIndex === 0;
      const numTranslations = isMachinery
        ? machineryTranslations.length + concordanceSearchResults.length
        : otherLocaleTranslations.length;

      if (numTranslations === 0) {
        return;
      }

      event.preventDefault();

      const currentIdx = editorState.selectedHelperElementIndex;
      const nextIdx =
        key === 40
          ? (currentIdx + 1) % numTranslations
          : (currentIdx - 1 + numTranslations) % numTranslations;

      dispatch(editor.actions.selectHelperElementIndex(nextIdx));

      if (isMachinery) {
        const len = machineryTranslations.length;
        const newTranslation =
          nextIdx < len
            ? machineryTranslations[nextIdx]
            : concordanceSearchResults[nextIdx - len];
        copyMachineryTranslation(newTranslation);
      } else {
        copyOtherLocaleTranslation(otherLocaleTranslations[nextIdx]);
      }
    }
  };
}
