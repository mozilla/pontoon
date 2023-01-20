import React, { useContext, useLayoutEffect } from 'react';
import { EditorActions, EditorData } from '~/context/Editor';

import { Locale } from '~/context/Locale';
import { useHandleShortcuts } from '~/core/editor';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';
import { searchBoxHasFocus } from '~/modules/search/components/SearchBox';

/**
 * Shows a generic translation form, a simple textarea.
 */
export function GenericTranslationForm(): React.ReactElement<'textarea'> | null {
  const { code, direction, script } = useContext(Locale);
  const readonly = useReadonlyEditor();
  const { setEditorFromInput } = useContext(EditorActions);
  const { activeInput, machinery, value } = useContext(EditorData);

  const handleShortcuts = useHandleShortcuts();

  // Focus the textarea when something changes.
  useLayoutEffect(() => {
    if (!searchBoxHasFocus()) {
      activeInput.current?.focus();
    }
  }, [machinery, value]);

  return (
    <textarea
      placeholder={
        readonly ? undefined : 'Type translation and press Enter to save'
      }
      readOnly={readonly}
      ref={activeInput}
      value={value[0]?.value}
      onKeyDown={handleShortcuts}
      onChange={(ev) => setEditorFromInput(ev.currentTarget.value)}
      dir={direction}
      lang={code}
      data-script={script}
    />
  );
}
