import { useLocalization } from '@fluent/react';
import React, { useCallback, useContext } from 'react';
import { EditorActions } from '~/context/Editor';
import { Locale } from '~/context/Locale';
import { useHandleShortcuts } from '~/core/editor';
import { useReadonlyEditor } from '~/hooks/useReadonlyEditor';

export type EditFieldProps = {
  activeInput: React.MutableRefObject<
    HTMLInputElement | HTMLTextAreaElement | null
  >;
  id?: string;
  placeholderId?: string;
  userInput: React.MutableRefObject<boolean>;
  value: string;
};

export function EditField({
  activeInput,
  id,
  placeholderId,
  userInput,
  value,
}: EditFieldProps) {
  const locale = useContext(Locale);
  const { l10n } = useLocalization();
  const { setEditorFromInput } = useContext(EditorActions);

  const handleChange: React.ChangeEventHandler<HTMLTextAreaElement> =
    useCallback(
      (ev) => {
        userInput.current = true;
        setEditorFromInput(ev.currentTarget.value);
      },
      [userInput, setEditorFromInput],
    );
  const handleFocus: React.FocusEventHandler<HTMLTextAreaElement> = useCallback(
    (ev) => (activeInput.current = ev.currentTarget),
    [activeInput],
  );
  const handleKeyDown = useHandleShortcuts();

  const props = {
    value,
    dir: locale.direction,
    lang: locale.code,
    'data-script': locale.script,
  };

  if (useReadonlyEditor()) {
    return <textarea readOnly {...props} />;
  }

  const placeholder = placeholderId
    ? l10n.getString(
        placeholderId,
        null,
        'Type translation and press Enter to saaaaaaasve',
      )
    : undefined;

  return (
    <textarea
      id={id}
      placeholder={placeholder}
      onChange={handleChange}
      onFocus={handleFocus}
      onKeyDown={handleKeyDown}
      {...props}
    />
  );
}
