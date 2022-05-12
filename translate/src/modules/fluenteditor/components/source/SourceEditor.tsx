import React from 'react';

import {
  EditorMenu,
  useClearEditor,
  useCopyOriginalIntoEditor,
  useSendTranslation,
  useUpdateTranslation,
} from '~/core/editor';
import { GenericTranslationForm } from '~/modules/genericeditor';

type Props = {
  ftlSwitch: React.ReactNode;
};

/**
 * Editor for complex Fluent strings.
 *
 * Displayed when the Rich Editor cannot handle the translation, or if a user
 * forces showing the Fluent source.
 */
export function SourceEditor({ ftlSwitch }: Props): React.ReactElement<any> {
  const clearEditor = useClearEditor();
  const copyOriginalIntoEditor = useCopyOriginalIntoEditor();
  const sendTranslation = useSendTranslation();
  const updateTranslation = useUpdateTranslation();

  return (
    <>
      <GenericTranslationForm
        sendTranslation={sendTranslation}
        updateTranslation={updateTranslation}
      />
      <EditorMenu
        firstItemHook={ftlSwitch}
        clearEditor={clearEditor}
        copyOriginalIntoEditor={copyOriginalIntoEditor}
        sendTranslation={sendTranslation}
      />
    </>
  );
}
