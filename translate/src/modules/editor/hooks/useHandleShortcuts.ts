import { useContext } from 'react';

import { EditorActions } from '~/context/Editor';
import { EntityView } from '~/context/EntityView';
import { FailedChecksData } from '~/context/FailedChecksData';
import { HelperSelection } from '~/context/HelperSelection';
import { MachineryTranslations } from '~/context/MachineryTranslations';
import { SearchData } from '~/context/SearchData';
import { UnsavedActions, UnsavedChanges } from '~/context/UnsavedChanges';
import { useAppSelector } from '~/hooks';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';
import { getPlainMessage } from '~/utils/message';

import { useCopyOriginalIntoEditor } from './useCopyOriginalIntoEditor';
import { useExistingTranslationGetter } from './useExistingTranslationGetter';
import { useSendTranslation } from './useSendTranslation';
import { useUpdateTranslationStatus } from './useUpdateTranslationStatus';

/**
 * Return a function to handle shortcuts in a translation form.
 */
export function useHandleShortcuts(): (event: React.KeyboardEvent) => void {
  const copyOriginalIntoEditor = useCopyOriginalIntoEditor();
  const sendTranslation = useSendTranslation();
  const updateTranslationStatus = useUpdateTranslationStatus();

  const { entity } = useContext(EntityView);
  const { resetUnsavedChanges } = useContext(UnsavedActions);
  const unsavedChanges = useContext(UnsavedChanges);
  const readonly = useReadonlyEditor();
  const { clearEditor, setEditorFromHelpers } = useContext(EditorActions);
  const getExistingTranslation = useExistingTranslationGetter();
  const { errors, source, warnings, resetFailedChecks } =
    useContext(FailedChecksData);
  const helperSelection = useContext(HelperSelection);

  const { translations: machineryTranslations } = useContext(
    MachineryTranslations,
  );
  const { results: concordanceSearchResults } = useContext(SearchData);
  const otherLocaleTranslations = useAppSelector(
    (state) => state.otherlocales.translations,
  );

  // Disable keyboard shortcuts when editor is in read only.
  if (readonly) {
    return () => {};
  }

  return (ev: React.KeyboardEvent) => {
    switch (ev.key) {
      // On Enter:
      //   - If unsaved changes popup is shown, proceed.
      //   - If failed checks popup is shown after approving a translation, approve it anyway.
      //   - In other cases, send current translation.
      case 'Enter':
        if (!ev.ctrlKey && !ev.shiftKey && !ev.altKey) {
          ev.preventDefault();

          const ignoreWarnings = errors.length + warnings.length > 0;

          if (unsavedChanges.onIgnore) {
            // There are unsaved changes, proceed.
            resetUnsavedChanges(true);
          } else if (typeof source === 'number') {
            // Approve anyway.
            updateTranslationStatus(source, 'approve', ignoreWarnings);
          } else {
            const existingTranslation = getExistingTranslation();
            if (existingTranslation && !existingTranslation.approved) {
              updateTranslationStatus(
                existingTranslation.pk,
                'approve',
                ignoreWarnings,
              );
            } else {
              sendTranslation(ignoreWarnings);
            }
          }
        }
        break;

      // On Esc, close unsaved changes and failed checks popups if open.
      case 'Escape':
        ev.preventDefault();
        if (unsavedChanges.onIgnore) {
          // Close unsaved changes popup
          resetUnsavedChanges(false);
        } else if (errors.length || warnings.length) {
          // Close failed checks popup
          resetFailedChecks();
        }
        break;

      // On Ctrl + Shift + C, copy the original translation.
      case 'C':
        if (ev.ctrlKey && ev.shiftKey && !ev.altKey) {
          ev.preventDefault();
          copyOriginalIntoEditor();
        }
        break;

      // On Ctrl + Shift + Backspace, clear the content.
      case 'Backspace':
        if (ev.ctrlKey && ev.shiftKey && !ev.altKey) {
          ev.preventDefault();
          clearEditor();
        }
        break;

      // On Ctrl + Shift + Up/Down, copy next/previous entry from active
      // helper tab (Machinery or Locales) into translation.
      case 'ArrowDown':
      case 'ArrowUp':
        if (ev.ctrlKey && ev.shiftKey && !ev.altKey) {
          const { tab, element, setElement } = helperSelection;
          const isMachinery = tab === 0;
          const numTranslations = isMachinery
            ? machineryTranslations.length + concordanceSearchResults.length
            : otherLocaleTranslations.length;

          if (numTranslations === 0) {
            return;
          }

          ev.preventDefault();

          const nextIdx =
            ev.key === 'ArrowDown'
              ? (element + 1) % numTranslations
              : (element - 1 + numTranslations) % numTranslations;
          setElement(nextIdx);

          if (isMachinery) {
            const len = machineryTranslations.length;
            const { translation, sources } =
              nextIdx < len
                ? machineryTranslations[nextIdx]
                : concordanceSearchResults[nextIdx - len];
            setEditorFromHelpers(translation, sources, true);
          } else {
            const { translation } = otherLocaleTranslations[nextIdx];
            setEditorFromHelpers(
              getPlainMessage(translation, entity.format),
              [],
              true,
            );
          }
        }
        break;
    }
  };
}
