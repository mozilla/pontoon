import { useAppDispatch, useAppSelector } from '~/hooks';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';
import {
  hide as hideUnsavedChanges,
  ignore as ignoreUnsavedChanges,
} from '~/modules/unsavedchanges/actions';
import { resetFailedChecks, selectHelperElementIndex } from '../actions';
import useClearEditor from './useClearEditor';
import useCopyMachineryTranslation from './useCopyMachineryTranslation';
import useCopyOriginalIntoEditor from './useCopyOriginalIntoEditor';
import useCopyOtherLocaleTranslation from './useCopyOtherLocaleTranslation';
import { useExistingTranslation } from './useExistingTranslation';
import useUpdateTranslationStatus from './useUpdateTranslationStatus';

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

  const clearEditor = useClearEditor();
  const copyMachineryTranslation = useCopyMachineryTranslation();
  const copyOriginalIntoEditor = useCopyOriginalIntoEditor();
  const copyOtherLocaleTranslation = useCopyOtherLocaleTranslation();
  const updateTranslationStatus = useUpdateTranslationStatus();

  const {
    errors,
    selectedHelperElementIndex,
    selectedHelperTabIndex,
    source,
    warnings,
  } = useAppSelector((state) => state.editor);
  const unsavedChangesShown = useAppSelector(
    (state) => state.unsavedchanges.shown,
  );
  const readonly = useReadonlyEditor();
  const existingTranslation = useExistingTranslation();

  const machineryTranslations = useAppSelector(
    (state) => state.machinery.translations,
  );
  const concordanceSearchResults = useAppSelector(
    (state) => state.machinery.searchResults,
  );
  const otherLocaleTranslations = useAppSelector(
    (state) => state.otherlocales.translations,
  );

  // Disable keyboard shortcuts when editor is in read only.
  if (readonly) {
    return () => {};
  }

  return (
    ev: React.KeyboardEvent<HTMLTextAreaElement>,
    sendTranslation: (ignoreWarnings?: boolean, translation?: string) => void,
    clearEditorCustom?: () => void,
    copyOriginalIntoEditorCustom?: () => void,
  ) => {
    switch (ev.key) {
      // On Enter:
      //   - If unsaved changes popup is shown, proceed.
      //   - If failed checks popup is shown after approving a translation, approve it anyway.
      //   - In other cases, send current translation.
      case 'Enter':
        if (!ev.ctrlKey && !ev.shiftKey && !ev.altKey) {
          ev.preventDefault();

          const ignoreWarnings = errors.length + warnings.length > 0;

          if (unsavedChangesShown) {
            // There are unsaved changes, proceed.
            dispatch(ignoreUnsavedChanges());
          } else if (typeof source === 'number') {
            // Approve anyway.
            updateTranslationStatus(source, 'approve', ignoreWarnings);
          } else if (existingTranslation && !existingTranslation.approved) {
            updateTranslationStatus(
              existingTranslation.pk,
              'approve',
              ignoreWarnings,
            );
          } else {
            sendTranslation(ignoreWarnings);
          }
        }
        break;

      // On Esc, close unsaved changes and failed checks popups if open.
      case 'Escape':
        ev.preventDefault();
        if (unsavedChangesShown) {
          // Close unsaved changes popup
          dispatch(hideUnsavedChanges());
        } else if (errors.length || warnings.length) {
          // Close failed checks popup
          dispatch(resetFailedChecks());
        }
        break;

      // On Ctrl + Shift + C, copy the original translation.
      case 'C':
        if (ev.ctrlKey && ev.shiftKey && !ev.altKey) {
          ev.preventDefault();
          (copyOriginalIntoEditorCustom || copyOriginalIntoEditor)();
        }
        break;

      // On Ctrl + Shift + Backspace, clear the content.
      case 'Backspace':
        if (ev.ctrlKey && ev.shiftKey && !ev.altKey) {
          ev.preventDefault();
          (clearEditorCustom || clearEditor)();
        }
        break;

      // On Ctrl + Shift + Up/Down, copy next/previous entry from active
      // helper tab (Machinery or Locales) into translation.
      case 'ArrowDown':
      case 'ArrowUp':
        if (ev.ctrlKey && ev.shiftKey && !ev.altKey) {
          const isMachinery = selectedHelperTabIndex === 0;
          const numTranslations = isMachinery
            ? machineryTranslations.length + concordanceSearchResults.length
            : otherLocaleTranslations.length;

          if (numTranslations === 0) {
            return;
          }

          ev.preventDefault();

          const nextIdx =
            ev.key === 'ArrowDown'
              ? (selectedHelperElementIndex + 1) % numTranslations
              : (selectedHelperElementIndex - 1 + numTranslations) %
                numTranslations;

          dispatch(selectHelperElementIndex(nextIdx));

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
        break;
    }
  };
}
