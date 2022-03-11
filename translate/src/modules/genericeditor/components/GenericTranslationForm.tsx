import * as React from 'react';

import { useAppDispatch, useAppSelector } from '~/hooks';
import * as editor from '~/core/editor';
import * as entities from '~/core/entities';

type Props = {
  sendTranslation: (ignoreWarnings?: boolean) => void;
  updateTranslation: (arg0: string) => void;
};

/**
 * Shows a generic translation form, a simple textarea.
 */
export default function GenericTranslationForm(
  props: Props,
): React.ReactElement<'textarea'> | null {
  const dispatch = useAppDispatch();

  const translation = useAppSelector((state) => state.editor.translation);
  const changeSource = useAppSelector((state) => state.editor.changeSource);
  const searchInputFocused = useAppSelector(
    (state) => state.search.searchInputFocused,
  );
  const locale = useAppSelector((state) => state.locale);
  const isReadOnlyEditor = useAppSelector((state) =>
    entities.selectors.isReadOnlyEditor(state),
  );
  const unsavedChangesExist = useAppSelector(
    (state) => state.unsavedchanges.exist,
  );

  const handleShortcutsFn = editor.useHandleShortcuts();

  const textareaRef = React.useRef<HTMLTextAreaElement>(null);

  // Focus the textarea when something changes.
  React.useLayoutEffect(() => {
    const input = textareaRef.current;

    if (!input || searchInputFocused) {
      return;
    }

    input.focus();

    if (changeSource !== 'internal') {
      input.setSelectionRange(0, 0);
    }
  }, [translation, changeSource, searchInputFocused]);

  // Reset checks when content of the editor changes and some changes have been made.
  React.useEffect(() => {
    if (unsavedChangesExist) {
      dispatch(editor.actions.resetFailedChecks());
    }
  }, [dispatch, translation, unsavedChangesExist]);

  // When the translation or the initial translation changes, check for unsaved changes.
  editor.useUpdateUnsavedChanges(false);

  // Replace selected content on external actions (for example, when a user clicks
  // on a placeable).
  editor.useReplaceSelectionContent((content: string) => {
    const input = textareaRef.current;

    if (!input) {
      return;
    }

    const newSelectionPos = input.selectionStart + content.length;

    // Update content in the textarea.
    input.setRangeText(content);

    // Put the cursor right after the newly inserted content.
    input.setSelectionRange(newSelectionPos, newSelectionPos);

    // Update the state to show the new content in the Editor.
    props.updateTranslation(input.value);
  });

  if (typeof translation !== 'string') {
    return null;
  }

  function handleChange(event: React.SyntheticEvent<HTMLTextAreaElement>) {
    props.updateTranslation(event.currentTarget.value);
  }

  function handleShortcuts(event: React.KeyboardEvent<HTMLTextAreaElement>) {
    handleShortcutsFn(event, props.sendTranslation);
  }

  return (
    <textarea
      placeholder={
        isReadOnlyEditor
          ? undefined
          : 'Type translation and press Enter to save'
      }
      readOnly={isReadOnlyEditor}
      ref={textareaRef}
      value={translation}
      onKeyDown={handleShortcuts}
      onChange={handleChange}
      dir={locale.direction}
      lang={locale.code}
      data-script={locale.script}
    />
  );
}
