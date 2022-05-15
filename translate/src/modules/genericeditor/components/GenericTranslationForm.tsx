import React, { useContext, useLayoutEffect, useRef } from 'react';
import { EditorActions, EditorData } from '~/context/Editor';

import { Locale } from '~/context/Locale';
import { useHandleShortcuts } from '~/core/editor';
import { useAppSelector } from '~/hooks';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';

/**
 * Shows a generic translation form, a simple textarea.
 */
export function GenericTranslationForm(): React.ReactElement<'textarea'> | null {
  const { code, direction, script } = useContext(Locale);
  const readonly = useReadonlyEditor();
  const { setEditorFromInput } = useContext(EditorActions);
  const { activeInput, value } = useContext(EditorData);
  const searchInputFocused = useAppSelector(
    (state) => state.search.searchInputFocused,
  );
  const userInput = useRef(false);

  const handleShortcuts = useHandleShortcuts();

  // Focus the textarea when something changes.
  useLayoutEffect(() => {
    const input = activeInput.current;
    if (input && !searchInputFocused) {
      input.focus();
      if (userInput.current) {
        userInput.current = false;
      } else {
        input.setSelectionRange(0, 0);
      }
    }
  }, [value, searchInputFocused]);

  return typeof value !== 'string' ? null : (
    <textarea
      placeholder={
        readonly ? undefined : 'Type translation and press Enter to save'
      }
      readOnly={readonly}
      ref={activeInput}
      value={value}
      onKeyDown={(ev) => {
        userInput.current = true;
        handleShortcuts(ev);
      }}
      onChange={(ev) => setEditorFromInput(ev.currentTarget.value)}
      dir={direction}
      lang={code}
      data-script={script}
    />
  );
}
